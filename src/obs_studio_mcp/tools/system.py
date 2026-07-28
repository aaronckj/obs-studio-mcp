"""System tools: stats, profiles, scene collections, hotkeys, health."""

from __future__ import annotations

from ..client import get_obs, preview


def register(mcp) -> None:
    @mcp.tool()
    def get_stats() -> dict:
        """OBS performance stats: CPU, memory, FPS, frame drops, disk space."""
        obs = get_obs()
        s = obs.call("get_stats")
        return {
            "cpu_percent": round(s.cpu_usage, 1),
            "memory_mb": round(s.memory_usage, 1),
            "fps": round(s.active_fps, 2),
            "render_missed_frames": s.render_skipped_frames,
            "output_skipped_frames": s.output_skipped_frames,
            "free_disk_mb": round(s.available_disk_space, 0),
        }

    @mcp.tool()
    def list_profiles() -> dict:
        """List OBS profiles and the current one."""
        obs = get_obs()
        res = obs.call("get_profile_list")
        return {"current": res.current_profile_name, "profiles": res.profiles}

    @mcp.tool()
    def switch_profile(profile: str, dry_run: bool = False) -> dict:
        """Switch OBS profile (stream settings bundle)."""
        if dry_run:
            return preview("switch_profile", {"profile": profile})
        obs = get_obs()
        obs.call("set_current_profile", profile)
        return {"profile": profile}

    @mcp.tool()
    def list_scene_collections() -> dict:
        """List scene collections and the current one."""
        obs = get_obs()
        res = obs.call("get_scene_collection_list")
        return {
            "current": res.current_scene_collection_name,
            "collections": res.scene_collections,
        }

    @mcp.tool()
    def switch_scene_collection(name: str, dry_run: bool = False) -> dict:
        """Switch scene collection (full scene layout bundle)."""
        if dry_run:
            return preview("switch_scene_collection", {"name": name})
        obs = get_obs()
        obs.call("set_current_scene_collection", name)
        return {"scene_collection": name}

    @mcp.tool()
    def trigger_hotkey(hotkey_name: str, dry_run: bool = False) -> dict:
        """Trigger an OBS hotkey by name (see get_hotkey_list in OBS docs)."""
        if dry_run:
            return preview("trigger_hotkey", {"hotkey_name": hotkey_name})
        obs = get_obs()
        obs.call("trigger_hot_key_by_name", hotkey_name)
        return {"triggered": hotkey_name}

    @mcp.tool()
    def health_check() -> dict:
        """Verify the OBS websocket connection and report versions."""
        try:
            obs = get_obs()
            v = obs.call("get_version")
            return {
                "status": "ok",
                "obs_version": v.obs_version,
                "websocket_version": v.obs_web_socket_version,
                "platform": v.platform,
            }
        except Exception as exc:  # noqa: BLE001 - health check reports, never raises
            return {"status": f"error: {exc}"}
