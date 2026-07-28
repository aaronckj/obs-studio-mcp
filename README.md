# obs-studio-mcp

An MCP (Model Context Protocol) server for controlling OBS Studio over
**obs-websocket v5**: scenes, sources, audio, text overlays, streaming,
recording, replay buffer, virtual camera, and performance stats.

- Talks to the obs-websocket server built into OBS 28+ (Tools → WebSocket
  Server Settings).
- Every mutating tool accepts `dry_run=true` and returns a preview instead
  of acting — useful guard rails when an agent drives your live stream.
- No secrets in this repo or in your MCP client config.

## Quick start

1. In OBS: **Tools → WebSocket Server Settings** → enable, note the port
   (default 4455) and password.
2. Provide connection settings via environment:

```bash
export OBS_MCP_HOST=127.0.0.1     # default
export OBS_MCP_PORT=4455          # default
export OBS_MCP_PASSWORD=yourpass  # via the default env backend
```

3. Add to your MCP client:

```bash
# Claude Code
claude mcp add obs -s user -- uvx obs-studio-mcp
```

## Tools

| Area | Tools |
|---|---|
| Scenes | `list_scenes`, `switch_scene`, `set_preview_scene`, `trigger_transition`, `set_studio_mode`, `list_scene_items`, `set_scene_item_visibility` |
| Sources | `list_inputs`, `get_audio_levels`, `set_mute`, `set_volume`, `update_text_source`, `screenshot_source`, `media_control` |
| Output | `stream_status`, `start_stream`, `stop_stream`, `record_status`, `start_record`, `stop_record`, `pause_record`, `save_replay`, `set_replay_buffer`, `set_virtual_cam` |
| System | `get_stats`, `list_profiles`, `switch_profile`, `list_scene_collections`, `switch_scene_collection`, `trigger_hotkey`, `health_check` |

`update_text_source` is handy for driving on-stream overlays from an agent —
question-of-the-day, now-playing, countdowns — anything rendered by a Text
source.

## Secret storage

The only secret is the websocket password.

| Backend | Select with | Reads |
|---|---|---|
| `env` (default) | — | `OBS_MCP_PASSWORD` |
| `file` | `OBS_MCP_SECRETS=file` | `~/.config/obs-studio-mcp/credentials.json` (0600) |
| `vaultproxy` | `OBS_MCP_SECRETS=vaultproxy` (+ `VAULTPROXY_URL`) | a Vaultwarden vault via a local vaultproxy HTTP API |

## Development

```bash
pip install -e '.[dev]'
ruff check src tests && pytest
```

Tests are fully offline (fake obs-websocket client).

## License

MIT
