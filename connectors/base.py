import json
import os
import time
from pathlib import Path
from typing import Any

# Vercel e outros ambientes serverless têm /tmp gravável; disco local pode ser read-only
_IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
CACHE_DIR = Path("/tmp/worldcup_cache") if _IS_SERVERLESS else Path(__file__).parent.parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Cache em memória como fallback rápido dentro da mesma invocação
_MEM_CACHE: dict[str, dict] = {}


class BaseConnector:
    name: str = "base"
    ttl: int = 300

    def is_configured(self) -> bool:
        raise NotImplementedError

    def _cache_key(self, key: str) -> str:
        return f"{self.name}_{key}"

    def _read_cache(self, key: str) -> Any | None:
        ck = self._cache_key(key)
        # memória primeiro
        if ck in _MEM_CACHE:
            entry = _MEM_CACHE[ck]
            if time.time() - entry["ts"] < entry["ttl"]:
                return entry["data"]

        # disco depois
        path = CACHE_DIR / f"{ck}.json"
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if time.time() - payload["ts"] < payload["ttl"]:
                    _MEM_CACHE[ck] = payload  # promove para memória
                    return payload["data"]
            except (KeyError, json.JSONDecodeError):
                pass
        return None

    def _write_cache(self, key: str, data: Any) -> None:
        ck = self._cache_key(key)
        entry = {"ts": time.time(), "ttl": self.ttl, "data": data}
        _MEM_CACHE[ck] = entry
        try:
            path = CACHE_DIR / f"{ck}.json"
            path.write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass  # sem disco gravável — ok, memória basta

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
