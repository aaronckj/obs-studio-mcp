import asyncio

from obs_studio_mcp.server import build_app

EXPECTED = {
    # scenes
    "list_scenes", "switch_scene", "set_preview_scene", "trigger_transition",
    "set_studio_mode", "list_scene_items", "set_scene_item_visibility",
    # sources
    "list_inputs", "get_audio_levels", "set_mute", "set_volume",
    "update_text_source", "screenshot_source", "media_control",
    # output
    "stream_status", "start_stream", "stop_stream", "record_status",
    "start_record", "stop_record", "pause_record", "save_replay",
    "set_replay_buffer", "set_virtual_cam",
    # filters/transforms/health
    "list_source_filters", "set_filter_enabled", "get_scene_item_transform",
    "set_scene_item_transform", "watch_health",
    # tuning
    "get_video_settings", "set_video_settings", "get_input_settings",
    "set_input_settings_json", "get_profile_parameter", "set_profile_parameter",
    "get_audio_sync_offset", "set_audio_sync_offset", "get_audio_monitoring",
    "set_audio_monitoring", "get_audio_tracks", "set_audio_tracks",
    # system
    "get_stats", "list_profiles", "switch_profile", "list_scene_collections",
    "switch_scene_collection", "trigger_hotkey", "health_check",
}


def test_all_tools_registered():
    app = build_app()
    tools = asyncio.run(app.list_tools())
    assert {t.name for t in tools} == EXPECTED
