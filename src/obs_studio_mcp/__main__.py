"""CLI entry: run the MCP server."""

from __future__ import annotations


def main() -> None:
    from .server import build_app

    build_app().run()


if __name__ == "__main__":
    main()
