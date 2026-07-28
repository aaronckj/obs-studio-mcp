"""Source filter and scene-item transform tools, plus a stream health sampler."""

from __future__ import annotations

import time

from ..client import get_obs, preview


def summarize_health(samples: list[dict]) -> dict:
    """Aggregate stat samples into a verdict (pure logic, unit-tested)."""
    if not samples:
        return {"verdict": "no samples"}
    n = len(samples)
    avg_fps = sum(s["fps"] for s in samples) / n
    cpu = sum(s["cpu"] for s in samples) / n
    render_dropped = samples[-1]["render_skipped"] - samples[0]["render_skipped"]
    output_dropped = samples[-1]["output_skipped"] - samples[0]["output_skipped"]
    frames = samples[-1].get("output_total", 0) - samples[0].get("output_total", 0)
    drop_pct = (output_dropped / frames * 100) if frames else 0.0
    issues = []
    if drop_pct > 1.0:
        issues.append(f"network/encoding drops {drop_pct:.1f}% (check bitrate/encoder)")
    if render_dropped > n:
        issues.append(f"renderer missed {render_dropped} frames (GPU overload)")
    if cpu > 80:
        issues.append(f"CPU {cpu:.0f}% (encoder overload risk)")
    return {
        "samples": n,
        "avg_fps": round(avg_fps, 1),
        "avg_cpu_percent": round(cpu, 1),
        "render_frames_missed": render_dropped,
        "output_frames_dropped": output_dropped,
        "drop_percent": round(drop_pct, 2),
        "verdict": "healthy" if not issues else "; ".join(issues),
    }


def register(mcp) -> None:
    @mcp.tool()
    def list_source_filters(source: str) -> list[dict]:
        """List filters on a source with enabled state."""
        obs = get_obs()
        res = obs.call("get_source_filter_list", source)
        return [
            {
                "name": f["filterName"],
                "kind": f["filterKind"],
                "enabled": f["filterEnabled"],
            }
            for f in res.filters
        ]

    @mcp.tool()
    def set_filter_enabled(
        source: str, filter_name: str, enabled: bool, dry_run: bool = False
    ) -> dict:
        """Enable or disable a named filter on a source."""
        if dry_run:
            return preview(
                "set_filter_enabled",
                {"source": source, "filter": filter_name, "enabled": enabled},
            )
        obs = get_obs()
        obs.call("set_source_filter_enabled", source, filter_name, enabled)
        return {"source": source, "filter": filter_name, "enabled": enabled}

    @mcp.tool()
    def get_scene_item_transform(scene: str, item_id: int) -> dict:
        """Get a scene item's position, scale, and crop."""
        obs = get_obs()
        res = obs.call("get_scene_item_transform", scene, item_id)
        t = res.scene_item_transform
        return {
            "x": t.get("positionX"),
            "y": t.get("positionY"),
            "scale_x": t.get("scaleX"),
            "scale_y": t.get("scaleY"),
            "width": t.get("width"),
            "height": t.get("height"),
        }

    @mcp.tool()
    def set_scene_item_transform(
        scene: str,
        item_id: int,
        x: float | None = None,
        y: float | None = None,
        scale_x: float | None = None,
        scale_y: float | None = None,
        dry_run: bool = False,
    ) -> dict:
        """Move/scale a scene item (item_id from list_scene_items). Only supplied
        fields change — e.g. scale_x/scale_y 0.5 halves a facecam."""
        changes: dict = {}
        if x is not None:
            changes["positionX"] = x
        if y is not None:
            changes["positionY"] = y
        if scale_x is not None:
            changes["scaleX"] = scale_x
        if scale_y is not None:
            changes["scaleY"] = scale_y
        if not changes:
            return {"error": "provide at least one of x, y, scale_x, scale_y"}
        if dry_run:
            return preview(
                "set_scene_item_transform",
                {"scene": scene, "item_id": item_id, **changes},
            )
        obs = get_obs()
        obs.call("set_scene_item_transform", scene, item_id, changes)
        return {"scene": scene, "item_id": item_id, "applied": changes}

    @mcp.tool()
    def watch_health(seconds: int = 10) -> dict:
        """Sample OBS stats for up to 60 seconds and report a stream-health
        verdict: dropped-frame %, GPU misses, CPU pressure."""
        seconds = max(2, min(60, seconds))
        obs = get_obs()
        samples = []
        for _ in range(seconds):
            s = obs.call("get_stats")
            sample = {
                "fps": s.active_fps,
                "cpu": s.cpu_usage,
                "render_skipped": s.render_skipped_frames,
                "output_skipped": s.output_skipped_frames,
            }
            try:
                stream = obs.call("get_stream_status")
                sample["output_total"] = getattr(stream, "output_total_frames", 0)
                sample["output_skipped"] = getattr(
                    stream, "output_skipped_frames", sample["output_skipped"]
                )
            except Exception:  # noqa: BLE001 - not streaming; stats-only sample
                sample["output_total"] = 0
            samples.append(sample)
            time.sleep(1)
        return summarize_health(samples)
