"""obs-websocket v5 connection wrapper."""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("obs_studio_mcp")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ObsError(RuntimeError):
    pass


class OBS:
    """Lazy holder for an obsws-python ReqClient (injectable for tests)."""

    def __init__(self, client: Any = None):
        self._client = client

    @property
    def client(self) -> Any:
        if self._client is None:
            import obsws_python as obs

            from .secrets import get_store

            host = os.environ.get("OBS_MCP_HOST", "127.0.0.1")
            port = int(os.environ.get("OBS_MCP_PORT", "4455"))
            password = get_store().get("password") or ""
            try:
                self._client = obs.ReqClient(
                    host=host, port=port, password=password, timeout=5
                )
            except Exception as exc:
                raise ObsError(
                    f"cannot connect to OBS websocket at {host}:{port} — is OBS running "
                    "with obs-websocket enabled (Tools → WebSocket Server Settings)? "
                    f"({exc})"
                ) from exc
        return self._client

    def call(self, method: str, *args: Any, **kwargs: Any) -> Any:
        try:
            result = getattr(self.client, method)(*args, **kwargs)
            logger.info("obs %s ok", method)
            return result
        except ObsError:
            raise
        except Exception as exc:
            logger.error("obs %s failed: %s", method, exc)
            raise ObsError(f"{method} failed: {exc}") from exc


def preview(action: str, would: dict) -> dict:
    return {"preview": True, "action": action, "would": would}


_obs: OBS | None = None


def get_obs() -> OBS:
    global _obs
    if _obs is None:
        _obs = OBS()
    return _obs
