import json
import time
from pathlib import Path
from typing import Any

CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class BaseConnector:
    name: str = "base"
    ttl: int = 300

    def is_configured(self) -> bool:
        raise NotImplementedError

    def _cache_path(self, key: str) -> Path:
        return CACHE_DIR / f"{self.name}_{key}.json"

    def _read_cache(self, key: str) -> Any | None:
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if time.time() - payload["ts"] < payload["ttl"]:
                return payload["data"]
        except (KeyError, json.JSONDecodeError):
            pass
        return None

    def _write_cache(self, key: str, data: Any) -> None:
        path = self._cache_path(key)
        path.write_text(
            json.dumps({"ts": time.time(), "ttl": self.ttl, "data": data}, ensure_ascii=False),
            encoding="utf-8",
        )

    def _get(self, key: str, fetcher) -> Any | None:
        cached = self._read_cache(key)
        if cached is not None:
            return cached
        if not self.is_configured():
            return None
        try:
            data = fetcher()
            if data is not None:
                self._write_cache(key, data)
            return data
        except Exception:
            return None
