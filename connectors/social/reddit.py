import httpx
from connectors.base import BaseConnector
from config import CACHE_TTL

SUBREDDITS = ["worldcup", "soccer", "futebol"]
USER_AGENT = "worldcup-analytics-engine/1.0"


class RedditConnector(BaseConnector):
    name = "reddit"
    ttl = CACHE_TTL["social"]

    def is_configured(self) -> bool:
        return True  # usa API pública JSON do Reddit

    def get_hot_posts(self, limit: int = 10) -> list[dict] | None:
        def fetch():
            posts = []
            for sub in SUBREDDITS:
                try:
                    r = httpx.get(
                        f"https://www.reddit.com/r/{sub}/hot.json",
                        params={"limit": limit},
                        headers={"User-Agent": USER_AGENT},
                        timeout=10,
                    )
                    r.raise_for_status()
                    for child in r.json().get("data", {}).get("children", []):
                        d = child["data"]
                        posts.append({
                            "subreddit": sub,
                            "title": d.get("title", ""),
                            "score": d.get("score", 0),
                            "comments": d.get("num_comments", 0),
                            "flair": d.get("link_flair_text", ""),
                            "url": f"https://reddit.com{d.get('permalink', '')}",
                        })
                except Exception:
                    continue
            return sorted(posts, key=lambda x: x["score"], reverse=True)[:20] or None
        return self._get("hot_posts", fetch)

    def search(self, query: str, limit: int = 10) -> list[dict] | None:
        def fetch():
            results = []
            for sub in SUBREDDITS:
                try:
                    r = httpx.get(
                        f"https://www.reddit.com/r/{sub}/search.json",
                        params={"q": query, "sort": "new", "restrict_sr": "on", "limit": limit},
                        headers={"User-Agent": USER_AGENT},
                        timeout=10,
                    )
                    r.raise_for_status()
                    for child in r.json().get("data", {}).get("children", []):
                        d = child["data"]
                        results.append({
                            "subreddit": sub,
                            "title": d.get("title", ""),
                            "score": d.get("score", 0),
                            "comments": d.get("num_comments", 0),
                        })
                except Exception:
                    continue
            return results or None
        key = f"search_{query[:30]}"
        return self._get(key, fetch)
