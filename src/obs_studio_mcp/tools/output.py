"""Streaming, recording, replay buffer, and virtual camera tools."""

from __future__ import annotations

from ..client import get_obs, preview


def register(mcp) -> None:
    @mcp.tool()
    def stream_status() -> dict:
        """Streaming state: live, duration, bytes, dropped frames."""
        obs = get_obs()
        s = obs.call("get_stream_status")
        return {
            "streaming": s.output_active,
            "reconnecting": getattr(s, "output_reconnecting", False),
            "duration_ms": getattr(s, "output_duration", 0),
            "total_frames": getattr(s, "output_total_frames", 0),
            "skipped_frames": getattr(s, "output_skipped_frames", 0),
        }

    @mcp.tool()
    def start_stream(dry_run: bool = False) -> dict:
        """Go live: start streaming to the configured service."""
        if dry_run:
            return preview("start_stream", {"note": "starts the live broadcast"})
        obs = get_obs()
        obs.call("start_stream")
        return {"streaming": True}

    @mcp.tool()
    def stop_stream(dry_run: bool = False) -> dict:
        """End the live stream."""
        if dry_run:
            return preview("stop_stream", {"note": "ends the live broadcast"})
        obs = get_obs()
        obs.call("stop_stream")
        return {"streaming": False}

    @mcp.tool()
    def record_status() -> dict:
        """Recording state: active, paused, duration, output path."""
        obs = get_obs()
        r = obs.call("get_record_status")
        return {
            "recording": r.output_active,
            "paused": getattr(r, "output_paused", False),
            "duration_ms": getattr(r, "output_duration", 0),
        }

    @mcp.tool()
    def start_record(dry_run: bool = False) -> dict:
        """Start recording."""
        if dry_run:
            return preview("start_record", {})
        obs = get_obs()
        obs.call("start_record")
        return {"recording": True}

    @mcp.tool()
    def stop_record(dry_run: bool = False) -> dict:
        """Stop recording; returns the saved file path."""
        if dry_run:
            return preview("stop_record", {})
        obs = get_obs()
        res = obs.call("stop_record")
        return {"recording": False, "output_path": getattr(res, "output_path", None)}

    @mcp.tool()
    def pause_record(paused: bool, dry_run: bool = False) -> dict:
        """Pause (true) or resume (false) the recording."""
        if dry_run:
            return preview("pause_record", {"paused": paused})
        obs = get_obs()
        obs.call("pause_record" if paused else "resume_record")
        return {"paused": paused}

    @mcp.tool()
    def save_replay(dry_run: bool = False) -> dict:
        """Save the replay buffer (must be running). Returns the clip path."""
        if dry_run:
            return preview("save_replay", {})
        obs = get_obs()
        obs.call("save_replay_buffer")
        res = obs.call("get_last_replay_buffer_replay")
        return {"saved": getattr(res, "saved_replay_path", None)}

    @mcp.tool()
    def set_replay_buffer(active: bool, dry_run: bool = False) -> dict:
        """Start (true) or stop (false) the replay buffer."""
        if dry_run:
            return preview("set_replay_buffer", {"active": active})
        obs = get_obs()
        obs.call("start_replay_buffer" if active else "stop_replay_buffer")
        return {"replay_buffer": active}

    @mcp.tool()
    def set_virtual_cam(active: bool, dry_run: bool = False) -> dict:
        """Start (true) or stop (false) the virtual camera."""
        if dry_run:
            return preview("set_virtual_cam", {"active": active})
        obs = get_obs()
        obs.call("start_virtual_cam" if active else "stop_virtual_cam")
        return {"virtual_cam": active}
