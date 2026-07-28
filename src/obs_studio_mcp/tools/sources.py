"""Input/source tools: audio, text overlays, media, screenshots."""

from __future__ import annotations

import base64
from pathlib import Path

from ..client import get_obs, preview


def register(mcp) -> None:
    @mcp.tool()
    def list_inputs() -> list[dict]:
        """List all inputs (sources) with their kinds."""
        obs = get_obs()
        res = obs.call("get_input_list")
        return [
            {"name": i["inputName"], "kind": i["inputKind"]} for i in res.inputs
        ]

    @mcp.tool()
    def get_audio_levels() -> list[dict]:
        """List audio inputs with mute state and volume (dB)."""
        obs = get_obs()
        inputs = obs.call("get_input_list").inputs
        out = []
        for i in inputs:
            name = i["inputName"]
            try:
                mute = obs.call("get_input_mute", name).input_muted
                vol = obs.call("get_input_volume", name)
                out.append(
                    {
                        "name": name,
                        "muted": mute,
                        "volume_db": round(vol.input_volume_db, 1),
                    }
                )
            except Exception:  # noqa: BLE001 - non-audio inputs raise; skip them
                continue
        return out

    @mcp.tool()
    def set_mute(input_name: str, muted: bool, dry_run: bool = False) -> dict:
        """Mute or unmute an audio input."""
        if dry_run:
            return preview("set_mute", {"input": input_name, "muted": muted})
        obs = get_obs()
        obs.call("set_input_mute", input_name, muted)
        return {"input": input_name, "muted": muted}

    @mcp.tool()
    def set_volume(input_name: str, volume_db: float, dry_run: bool = False) -> dict:
        """Set an audio input's volume in dB (0 = unity, negative = quieter)."""
        if dry_run:
            return preview("set_volume", {"input": input_name, "volume_db": volume_db})
        obs = get_obs()
        obs.call("set_input_volume", input_name, vol_db=volume_db)
        return {"input": input_name, "volume_db": volume_db}

    @mcp.tool()
    def update_text_source(input_name: str, text: str, dry_run: bool = False) -> dict:
        """Set the text of a Text (GDI+/FreeType) source — e.g. an on-stream overlay
        line like a giveaway question or now-playing label."""
        if dry_run:
            return preview("update_text_source", {"input": input_name, "text": text})
        obs = get_obs()
        obs.call("set_input_settings", input_name, {"text": text}, True)
        return {"input": input_name, "text": text}

    @mcp.tool()
    def screenshot_source(
        source: str, file_path: str, width: int | None = None, dry_run: bool = False
    ) -> dict:
        """Save a PNG screenshot of a source (or scene) to a local file."""
        if dry_run:
            return preview("screenshot_source", {"source": source, "file_path": file_path})
        obs = get_obs()
        kwargs = {"name": source, "img_format": "png", "quality": -1}
        if width:
            kwargs["width"] = width
        res = obs.call("get_source_screenshot", **kwargs)
        data = res.image_data.split(",", 1)[-1]
        Path(file_path).write_bytes(base64.b64decode(data))
        return {"saved": file_path, "source": source}

    @mcp.tool()
    def media_control(input_name: str, action: str, dry_run: bool = False) -> dict:
        """Control a media source. action: play|pause|restart|stop|next|previous."""
        actions = {
            "play": "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY",
            "pause": "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PAUSE",
            "restart": "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART",
            "stop": "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP",
            "next": "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_NEXT",
            "previous": "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PREVIOUS",
        }
        if action not in actions:
            return {"error": f"action must be one of {sorted(actions)}"}
        if dry_run:
            return preview("media_control", {"input": input_name, "action": action})
        obs = get_obs()
        obs.call("trigger_media_input_action", input_name, actions[action])
        return {"input": input_name, "action": action}
