import feedparser
from connectors.base import BaseConnector
from config import CACHE_TTL

RSS_FEEDS = {
    "BBC Sport": "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "ESPN Soccer": "https://www.espn.com/espn/rss/soccer/news",
    "Goal.com": "https://www.goal.com/feeds/en/news",
    "AS.com": "https://as.com/rss/tags/mundial.xml",
}


class RSSConnector(BaseConnector):
    name = "rss"
    ttl = CACHE_TTL["news"]

    def is_configured(self) -> bool:
        return True  # sem API key necessária

    def get_headlines(self, max_per_feed: int = 5) -> list[dict] | None:
        def fetch():
            items = []
            for source, url in RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:max_per_feed]:
                        items.append({
                            "source": source,
                            "title": entry.get("title", ""),
                            "summary": entry.get("summary", "")[:300],
                            "link": entry.get("link", ""),
                            "published": entry.get("published", ""),
                        })
                except Exception:
                    continue
            return items or None
        return self._get("headlines", fetch)
