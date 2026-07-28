"""Video/audio/encoder tuning tools.

Video settings and input settings apply live; profile parameters write to
the active profile's config (encoder, bitrate) and generally take effect
when the output (stream/recording) next starts.
"""

from __future__ import annotations

from ..client import get_obs, preview

MONITOR_TYPES = {
    "none": "OBS_MONITORING_TYPE_NONE",
    "monitor_only": "OBS_MONITORING_TYPE_MONITOR_ONLY",
    "monitor_and_output": "OBS_MONITORING_TYPE_MONITOR_AND_OUTPUT",
}


def register(mcp) -> None:
    @mcp.tool()
    def get_video_settings() -> dict:
        """Canvas resolution, output (scaled) resolution, and FPS."""
        obs = get_obs()
        v = obs.call("get_video_settings")
        return {
            "canvas": f"{v.base_width}x{v.base_height}",
            "output": f"{v.output_width}x{v.output_height}",
            "fps": round(v.fps_numerator / v.fps_denominator, 3),
        }

    @mcp.tool()
    def set_video_settings(
        canvas_width: int | None = None,
        canvas_height: int | None = None,
        output_width: int | None = None,
        output_height: int | None = None,
        fps: int | None = None,
        dry_run: bool = False,
    ) -> dict:
        """Change canvas/output resolution and/or FPS (integer fps, e.g. 30/60).
        Only supplied fields change. Cannot change while streaming/recording."""
        obs = get_obs()
        cur = obs.call("get_video_settings")
        args = {
            "numerator": fps if fps else cur.fps_numerator,
            "denominator": 1 if fps else cur.fps_denominator,
            "base_width": canvas_width or cur.base_width,
            "base_height": canvas_height or cur.base_height,
            "out_width": output_width or cur.output_width,
            "out_height": output_height or cur.output_height,
        }
        if dry_run:
            return preview("set_video_settings", args)
        obs.call("set_video_settings", *args.values())
        return {"applied": args}

    @mcp.tool()
    def get_input_settings(input_name: str) -> dict:
        """An input's full settings object (e.g. capture card resolution/format)
        plus its kind — inspect before tweaking with set_input_settings_json."""
        obs = get_obs()
        r = obs.call("get_input_settings", input_name)
        return {"kind": r.input_kind, "settings": r.input_settings}

    @mcp.tool()
    def set_input_settings_json(
        input_name: str, settings: dict, dry_run: bool = False
    ) -> dict:
        """Merge a settings dict into an input (keys from get_input_settings).
        Example: capture card {"resolution": "1920x1080"} — device-dependent."""
        if dry_run:
            return preview("set_input_settings_json", {"input": input_name, "settings": settings})
        obs = get_obs()
        obs.call("set_input_settings", input_name, settings, True)
        return {"input": input_name, "merged": settings}

    @mcp.tool()
    def get_profile_parameter(category: str, name: str) -> dict:
        """Read a profile config value. Common: (SimpleOutput, VBitrate),
        (SimpleOutput, StreamEncoder), (Output, Mode), (AdvOut, Encoder),
        (Audio, SampleRate)."""
        obs = get_obs()
        r = obs.call("get_profile_parameter", category, name)
        return {
            "category": category,
            "name": name,
            "value": r.parameter_value,
            "default": r.default_parameter_value,
        }

    @mcp.tool()
    def set_profile_parameter(
        category: str, name: str, value: str, dry_run: bool = False
    ) -> dict:
        """Write a profile config value (e.g. SimpleOutput/VBitrate 6000).
        Takes effect when the output next starts."""
        if dry_run:
            return preview(
                "set_profile_parameter", {"category": category, "name": name, "value": value}
            )
        obs = get_obs()
        obs.call("set_profile_parameter", category, name, value)
        return {"set": f"{category}/{name}", "value": value, "note": "applies on next output start"}

    @mcp.tool()
    def get_audio_sync_offset(input_name: str) -> dict:
        """An audio input's sync offset in ms (fix lip-sync drift)."""
        obs = get_obs()
        r = obs.call("get_input_audio_sync_offset", input_name)
        return {"input": input_name, "offset_ms": r.input_audio_sync_offset}

    @mcp.tool()
    def set_audio_sync_offset(input_name: str, offset_ms: int, dry_run: bool = False) -> dict:
        """Set an audio input's sync offset in ms (-950..20000)."""
        if dry_run:
            return preview("set_audio_sync_offset", {"input": input_name, "offset_ms": offset_ms})
        obs = get_obs()
        obs.call("set_input_audio_sync_offset", input_name, offset_ms)
        return {"input": input_name, "offset_ms": offset_ms}

    @mcp.tool()
    def get_audio_monitoring(input_name: str) -> dict:
        """How an input is monitored: none | monitor_only | monitor_and_output."""
        obs = get_obs()
        r = obs.call("get_input_audio_monitor_type", input_name)
        rev = {v: k for k, v in MONITOR_TYPES.items()}
        return {"input": input_name, "monitoring": rev.get(r.monitor_type, r.monitor_type)}

    @mcp.tool()
    def set_audio_monitoring(input_name: str, monitoring: str, dry_run: bool = False) -> dict:
        """Set input monitoring: none | monitor_only | monitor_and_output."""
        if monitoring not in MONITOR_TYPES:
            return {"error": f"monitoring must be one of {sorted(MONITOR_TYPES)}"}
        if dry_run:
            return preview(
                "set_audio_monitoring", {"input": input_name, "monitoring": monitoring}
            )
        obs = get_obs()
        obs.call("set_input_audio_monitor_type", input_name, MONITOR_TYPES[monitoring])
        return {"input": input_name, "monitoring": monitoring}

    @mcp.tool()
    def get_audio_tracks(input_name: str) -> dict:
        """Which of the 6 output tracks an input feeds (recording/stream mixes)."""
        obs = get_obs()
        r = obs.call("get_input_audio_tracks", input_name)
        return {"input": input_name, "tracks": r.input_audio_tracks}

    @mcp.tool()
    def set_audio_tracks(input_name: str, tracks: dict, dry_run: bool = False) -> dict:
        """Set track membership, e.g. {"1": true, "2": false, ...}."""
        if dry_run:
            return preview("set_audio_tracks", {"input": input_name, "tracks": tracks})
        obs = get_obs()
        obs.call("set_input_audio_tracks", input_name, tracks)
        return {"input": input_name, "tracks": tracks}
