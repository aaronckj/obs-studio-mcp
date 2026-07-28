"""Scene and transition tools."""

from __future__ import annotations

from ..client import get_obs, preview


def register(mcp) -> None:
    @mcp.tool()
    def list_scenes() -> dict:
        """List scenes and the current program/preview scene."""
        obs = get_obs()
        res = obs.call("get_scene_list")
        return {
            "current_program": res.current_program_scene_name,
            "current_preview": getattr(res, "current_preview_scene_name", None),
            "scenes": [s["sceneName"] for s in reversed(res.scenes)],
        }

    @mcp.tool()
    def switch_scene(scene: str, dry_run: bool = False) -> dict:
        """Switch the program output to a scene (immediate cut on program)."""
        if dry_run:
            return preview("switch_scene", {"scene": scene})
        obs = get_obs()
        obs.call("set_current_program_scene", scene)
        return {"program_scene": scene}

    @mcp.tool()
    def set_preview_scene(scene: str, dry_run: bool = False) -> dict:
        """Set the preview scene (studio mode)."""
        if dry_run:
            return preview("set_preview_scene", {"scene": scene})
        obs = get_obs()
        obs.call("set_current_preview_scene", scene)
        return {"preview_scene": scene}

    @mcp.tool()
    def trigger_transition(dry_run: bool = False) -> dict:
        """Trigger the studio-mode transition (preview → program)."""
        if dry_run:
            return preview("trigger_transition", {})
        obs = get_obs()
        obs.call("trigger_studio_mode_transition")
        return {"transitioned": True}

    @mcp.tool()
    def set_studio_mode(enabled: bool, dry_run: bool = False) -> dict:
        """Enable or disable studio mode."""
        if dry_run:
            return preview("set_studio_mode", {"enabled": enabled})
        obs = get_obs()
        obs.call("set_studio_mode_enabled", enabled)
        return {"studio_mode": enabled}

    @mcp.tool()
    def list_scene_items(scene: str) -> list[dict]:
        """List the items (sources) inside a scene with visibility state."""
        obs = get_obs()
        res = obs.call("get_scene_item_list", scene)
        return [
            {
                "id": i["sceneItemId"],
                "source": i["sourceName"],
                "visible": i["sceneItemEnabled"],
            }
            for i in res.scene_items
        ]

    @mcp.tool()
    def set_scene_item_visibility(
        scene: str, item_id: int, visible: bool, dry_run: bool = False
    ) -> dict:
        """Show or hide a scene item (item_id from list_scene_items)."""
        if dry_run:
            return preview(
                "set_scene_item_visibility",
                {"scene": scene, "item_id": item_id, "visible": visible},
            )
        obs = get_obs()
        obs.call("set_scene_item_enabled", scene, item_id, visible)
        return {"scene": scene, "item_id": item_id, "visible": visible}
