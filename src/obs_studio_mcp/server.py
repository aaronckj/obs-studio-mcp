"""FastMCP app assembly."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .tools import build, filters, output, scenes, sfx, sources, system, tuning


def build_app() -> FastMCP:
    mcp = FastMCP(
        "obs-studio",
        instructions=(
            "Control a local OBS Studio over obs-websocket v5: scenes, sources, "
            "audio, text overlays, streaming, recording, replay buffer, virtual "
            "camera, and performance stats. Every mutating tool accepts "
            "dry_run=True to preview without acting."
        ),
    )
    for module in (scenes, sources, filters, sfx, build, output, system, tuning):
        module.register(mcp)
    return mcp
