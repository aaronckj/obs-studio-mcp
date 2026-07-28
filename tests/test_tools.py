import asyncio
import json
from types import SimpleNamespace

import obs_studio_mcp.client as client_mod
from obs_studio_mcp.client import OBS
from obs_studio_mcp.server import build_app


class FakeReqClient:
    """Records calls; returns canned obsws-style responses."""

    def __init__(self):
        self.calls = []

    def _record(self, name, *args, **kwargs):
        self.calls.append((name, args, kwargs))

    def get_scene_list(self):
        self._record("get_scene_list")
        return SimpleNamespace(
            current_program_scene_name="Game",
            current_preview_scene_name="BRB",
            scenes=[{"sceneName": "BRB"}, {"sceneName": "Game"}],
        )

    def set_current_program_scene(self, scene):
        self._record("set_current_program_scene", scene)

    def get_stream_status(self):
        self._record("get_stream_status")
        return SimpleNamespace(
            output_active=True,
            output_reconnecting=False,
            output_duration=61000,
            output_total_frames=3660,
            output_skipped_frames=2,
        )

    def set_input_mute(self, name, muted):
        self._record("set_input_mute", name, muted)

    def set_input_settings(self, name, settings, overlay):
        self._record("set_input_settings", name, settings, overlay)


def call_tool(app, name, args=None):
    result = asyncio.run(app.call_tool(name, args or {}))
    # FastMCP returns a list of content blocks; first is the JSON text.
    blocks = result[0] if isinstance(result, tuple) else result
    return json.loads(blocks[0].text)


def make_app(fake):
    client_mod._obs = OBS(client=fake)
    return build_app()


def teardown_function():
    client_mod._obs = None


def test_list_scenes_shapes_response():
    fake = FakeReqClient()
    app = make_app(fake)
    out = call_tool(app, "list_scenes")
    assert out["current_program"] == "Game"
    assert out["scenes"] == ["Game", "BRB"]


def test_switch_scene_calls_client():
    fake = FakeReqClient()
    app = make_app(fake)
    out = call_tool(app, "switch_scene", {"scene": "BRB"})
    assert out == {"program_scene": "BRB"}
    assert ("set_current_program_scene", ("BRB",), {}) in fake.calls


def test_switch_scene_dry_run_does_not_call():
    fake = FakeReqClient()
    app = make_app(fake)
    out = call_tool(app, "switch_scene", {"scene": "BRB", "dry_run": True})
    assert out["preview"] is True
    assert fake.calls == []


def test_stream_status_shapes_response():
    fake = FakeReqClient()
    app = make_app(fake)
    out = call_tool(app, "stream_status")
    assert out["streaming"] is True
    assert out["skipped_frames"] == 2


def test_update_text_source():
    fake = FakeReqClient()
    app = make_app(fake)
    out = call_tool(app, "update_text_source", {"input_name": "Question", "text": "Q: fave boss?"})
    assert out["text"] == "Q: fave boss?"
    assert ("set_input_settings", ("Question", {"text": "Q: fave boss?"}, True), {}) in fake.calls
