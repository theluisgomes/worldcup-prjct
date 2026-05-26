import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Copa do Mundo 2026 — IDs de competição por API
FOOTBALL_DATA_COMPETITION_ID = "WC"   # football-data.org
API_FOOTBALL_LEAGUE_ID = 1            # API-Football (World Cup)
API_FOOTBALL_SEASON = 2026

CACHE_TTL = {
    "sports": 300,    # 5 min
    "news": 900,      # 15 min
    "social": 1800,   # 30 min
}
