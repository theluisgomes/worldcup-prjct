import httpx
from connectors.base import BaseConnector
from config import TWITTER_BEARER_TOKEN, CACHE_TTL

BASE_URL = "https://api.twitter.com/2"


class TwitterConnector(BaseConnector):
    name = "twitter"
    ttl = CACHE_TTL["social"]

    def is_configured(self) -> bool:
        return bool(TWITTER_BEARER_TOKEN)

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

    def search_recent(self, query: str, max_results: int = 20) -> list[dict] | None:
        def fetch():
            safe_query = f"({query}) -is:retweet lang:en OR lang:pt"
            r = httpx.get(
                f"{BASE_URL}/tweets/search/recent",
                headers=self._headers(),
                params={
                    "query": safe_query,
                    "max_results": max_results,
                    "tweet.fields": "public_metrics,author_id,created_at",
                },
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            return [
                {
                    "text": t.get("text", ""),
                    "likes": t.get("public_metrics", {}).get("like_count", 0),
                    "retweets": t.get("public_metrics", {}).get("retweet_count", 0),
                    "replies": t.get("public_metrics", {}).get("reply_count", 0),
                    "created_at": t.get("created_at", "")[:16],
                }
                for t in data.get("data", [])
            ] or None
        key = f"search_{query[:30]}"
        return self._get(key, fetch)

    def get_trending_worldcup(self) -> list[dict] | None:
        return self.search_recent("FIFA World Cup 2026 OR #WorldCup2026", max_results=25)
