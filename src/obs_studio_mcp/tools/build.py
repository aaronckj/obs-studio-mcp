"""Scene-building tools: create scenes, add sources of any kind, reorder,
duplicate existing sources into scenes, add scene items, remove scenes.

Placement is by coordinates — pair with screenshot_source to verify and
nudge. Common input kinds:
  dshow_input          capture card / webcam (Video Capture Device)
  wasapi_input_capture microphone / line-in
  wasapi_output_capture desktop audio
  image_source         static image (settings: {"file": "C:/path.png"})
  ffmpeg_source        video/audio file (settings: {"local_file": "..."})
  vlc_source           playlist (settings: {"playlist": [...]})
  text_gdiplus_v3      text (settings: {"text": "...", "font": {...}})
  browser_source       web/overlay (settings: {"url": "...", "width":.., "height":..})
  color_source_v3      solid color background
"""

from __future__ import annotations

from ..client import get_obs, preview


def register(mcp) -> None:
    @mcp.tool()
    def create_scene(name: str, dry_run: bool = False) -> dict:
        """Create a new empty scene."""
        if dry_run:
            return preview("create_scene", {"name": name})
        obs = get_obs()
        obs.call("create_scene", name)
        return {"created_scene": name}

    @mcp.tool()
    def remove_scene(name: str, dry_run: bool = False) -> dict:
        """Delete a scene (its unique sources are removed; shared ones survive)."""
        if dry_run:
            return preview("remove_scene", {"name": name})
        obs = get_obs()
        obs.call("remove_scene", name)
        return {"removed_scene": name}

    @mcp.tool()
    def add_source(
        scene: str,
        name: str,
        kind: str,
        settings: dict | None = None,
        dry_run: bool = False,
    ) -> dict:
        """Create a new input and add it to a scene. kind is an OBS input kind
        (see module doc). settings is kind-specific (e.g. image_source
        {"file": "C:/logo.png"}). Returns the new scene-item id for transforms."""
        if dry_run:
            return preview(
                "add_source", {"scene": scene, "name": name, "kind": kind, "settings": settings}
            )
        obs = get_obs()
        r = obs.call("create_input", scene, name, kind, settings or {}, True)
        return {"scene": scene, "name": name, "kind": kind, "item_id": r.scene_item_id}

    @mcp.tool()
    def list_input_kinds() -> list[str]:
        """List the input kinds this OBS build supports (for add_source)."""
        obs = get_obs()
        return list(obs.call("get_input_kind_list", False).input_kinds)

    @mcp.tool()
    def add_existing_source(scene: str, source_name: str, dry_run: bool = False) -> dict:
        """Add an EXISTING source to another scene (shared reference — a camera
        or overlay reused across scenes). Returns the new scene-item id."""
        if dry_run:
            return preview("add_existing_source", {"scene": scene, "source": source_name})
        obs = get_obs()
        r = obs.call("create_scene_item", scene, source_name, True)
        return {"scene": scene, "source": source_name, "item_id": r.scene_item_id}

    @mcp.tool()
    def duplicate_scene(source_scene: str, new_name: str, dry_run: bool = False) -> dict:
        """Duplicate a scene (great starting point: copy 'Normal Stream' then tweak)."""
        if dry_run:
            return preview("duplicate_scene", {"from": source_scene, "to": new_name})
        obs = get_obs()
        # obs-websocket has no direct scene-duplicate; recreate with shared items.
        obs.call("create_scene", new_name)
        items = obs.call("get_scene_item_list", source_scene).scene_items
        added = 0
        for it in reversed(items):
            obs.call("create_scene_item", new_name, it["sourceName"], it["sceneItemEnabled"])
            added += 1
        return {"duplicated_to": new_name, "items": added}

    @mcp.tool()
    def set_source_order(scene: str, item_id: int, index: int, dry_run: bool = False) -> dict:
        """Set a scene item's stacking index (0 = bottom). Controls layering."""
        if dry_run:
            return preview("set_source_order", {"scene": scene, "item_id": item_id, "index": index})
        obs = get_obs()
        obs.call("set_scene_item_index", scene, item_id, index)
        return {"scene": scene, "item_id": item_id, "index": index}
