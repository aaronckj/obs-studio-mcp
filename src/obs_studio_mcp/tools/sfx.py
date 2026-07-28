"""One-shot sound effects: create/list SFX media sources and fire them.

Sound-effect files live in a dedicated hidden scene (default "SFX"). Each
effect is a media source that is added stopped; play_sfx restarts it from
the top so rapid re-triggers work. The SFX scene is never shown on program
— the audio plays into the mix regardless of scene visibility.
"""

from __future__ import annotations

from pathlib import PurePath

from ..client import get_obs, preview

RESTART = "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART"
STOP = "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP"


def register(mcp) -> None:
    @mcp.tool()
    def add_sfx(name: str, file_path: str, scene: str = "SFX", dry_run: bool = False) -> dict:
        """Register a sound effect: creates the SFX scene if needed and adds a
        media source `name` pointing at file_path (a local audio/video file on
        the OBS machine). Added stopped; fire it later with play_sfx."""
        if dry_run:
            return preview("add_sfx", {"name": name, "file_path": file_path, "scene": scene})
        obs = get_obs()
        scenes = obs.call("get_scene_list").scenes
        if not any(s["sceneName"] == scene for s in scenes):
            obs.call("create_scene", scene)
        obs.call(
            "create_input",
            scene,
            name,
            "ffmpeg_source",
            {"local_file": file_path, "restart_on_activate": False},
            False,
        )
        return {"added": name, "scene": scene, "file": PurePath(file_path).name}

    @mcp.tool()
    def list_sfx(scene: str = "SFX") -> list[dict]:
        """List registered sound effects in the SFX scene."""
        obs = get_obs()
        try:
            items = obs.call("get_scene_item_list", scene).scene_items
        except Exception:  # noqa: BLE001 - scene not created yet
            return []
        return [{"name": i["sourceName"], "id": i["sceneItemId"]} for i in items]

    @mcp.tool()
    def play_sfx(name: str, dry_run: bool = False) -> dict:
        """Play a registered sound effect once, from the top (restarts if already
        playing so rapid re-triggers work). Audio plays into the mix regardless
        of the current scene."""
        if dry_run:
            return preview("play_sfx", {"name": name})
        obs = get_obs()
        obs.call("trigger_media_input_action", name, RESTART)
        return {"played": name}

    @mcp.tool()
    def stop_sfx(name: str, dry_run: bool = False) -> dict:
        """Stop a currently playing sound effect."""
        if dry_run:
            return preview("stop_sfx", {"name": name})
        obs = get_obs()
        obs.call("trigger_media_input_action", name, STOP)
        return {"stopped": name}

    @mcp.tool()
    def remove_sfx(name: str, dry_run: bool = False) -> dict:
        """Delete a registered sound effect (removes the media input)."""
        if dry_run:
            return preview("remove_sfx", {"name": name})
        obs = get_obs()
        obs.call("remove_input", name)
        return {"removed": name}
