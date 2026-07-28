"""Pluggable secret storage for the OBS websocket password.

Selected via OBS_MCP_SECRETS (file | env | vaultproxy, default env→file):
the websocket password is the only secret this server ever needs.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

DEFAULT_PATH = Path.home() / ".config" / "obs-studio-mcp" / "credentials.json"


class SecretStore:
    def get(self, key: str) -> str | None:
        raise NotImplementedError

    def set(self, key: str, value: str) -> None:
        raise NotImplementedError


class FileStore(SecretStore):
    def __init__(self, path: Path | None = None):
        self.path = Path(path or DEFAULT_PATH)

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text())

    def get(self, key: str) -> str | None:
        return self._load().get(key)

    def set(self, key: str, value: str) -> None:
        data = self._load()
        data[key] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2))
        self.path.chmod(0o600)


class EnvStore(SecretStore):
    def get(self, key: str) -> str | None:
        return os.environ.get(f"OBS_MCP_{key.upper()}")

    def set(self, key: str, value: str) -> None:
        raise NotImplementedError("env secret backend is read-only")


class VaultproxyStore(SecretStore):
    def __init__(self, base_url: str | None = None):
        self.base_url = (
            base_url or os.environ.get("VAULTPROXY_URL", "http://127.0.0.1:8199")
        ).rstrip("/")

    def _request(self, method: str, key: str, body: dict | None = None) -> dict:
        req = Request(
            f"{self.base_url}/items/obs-studio-mcp%2F{key}",
            method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"content-type": "application/json"},
        )
        try:
            with urlopen(req, timeout=10) as resp:
                raw = resp.read()
        except URLError as exc:
            raise RuntimeError(
                f"vaultproxy unreachable at {self.base_url}: {exc.reason}"
            ) from exc
        return json.loads(raw) if raw else {}

    def get(self, key: str) -> str | None:
        try:
            return self._request("GET", key).get("value")
        except RuntimeError:
            raise
        except Exception:
            return None

    def set(self, key: str, value: str) -> None:
        self._request("PUT", key, {"value": value})


def get_store() -> SecretStore:
    backend = os.environ.get("OBS_MCP_SECRETS", "env")
    if backend == "file":
        return FileStore()
    if backend == "env":
        return EnvStore()
    if backend == "vaultproxy":
        return VaultproxyStore()
    raise ValueError(f"unknown OBS_MCP_SECRETS backend: {backend!r} (file|env|vaultproxy)")
