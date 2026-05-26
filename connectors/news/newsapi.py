import httpx
from connectors.base import BaseConnector
from config import NEWSAPI_KEY, CACHE_TTL

BASE_URL = "https://newsapi.org/v2"


class NewsAPIConnector(BaseConnector):
    name = "newsapi"
    ttl = CACHE_TTL["news"]

    def is_configured(self) -> bool:
        return bool(NEWSAPI_KEY)

    def get_headlines(self, query: str = "FIFA World Cup 2026", max_results: int = 10) -> list[dict] | None:
        def fetch():
            r = httpx.get(
                f"{BASE_URL}/everything",
                params={
                    "q": query,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "pageSize": max_results,
                    "apiKey": NEWSAPI_KEY,
                },
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            return [
                {
                    "source": a.get("source", {}).get("name", ""),
                    "title": a.get("title", ""),
                    "description": (a.get("description") or "")[:300],
                    "url": a.get("url", ""),
                    "published": a.get("publishedAt", "")[:10],
                }
                for a in data.get("articles", [])
            ] or None
        return self._get(f"headlines_{query[:30]}", fetch)
