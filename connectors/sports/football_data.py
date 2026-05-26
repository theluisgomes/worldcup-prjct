import httpx
from connectors.base import BaseConnector
from config import FOOTBALL_DATA_API_KEY, FOOTBALL_DATA_COMPETITION_ID, CACHE_TTL

BASE_URL = "https://api.football-data.org/v4"


class FootballDataConnector(BaseConnector):
    name = "football_data"
    ttl = CACHE_TTL["sports"]

    def is_configured(self) -> bool:
        return bool(FOOTBALL_DATA_API_KEY)

    def _headers(self) -> dict:
        return {"X-Auth-Token": FOOTBALL_DATA_API_KEY}

    def _fetch(self, path: str) -> dict | None:
        r = httpx.get(f"{BASE_URL}{path}", headers=self._headers(), timeout=10)
        r.raise_for_status()
        return r.json()

    def get_standings(self) -> list[dict] | None:
        def fetch():
            data = self._fetch(f"/competitions/{FOOTBALL_DATA_COMPETITION_ID}/standings")
            if not data:
                return None
            groups = []
            for standing in data.get("standings", []):
                groups.append({
                    "group": standing.get("group") or standing.get("stage"),
                    "table": [
                        {
                            "pos": row["position"],
                            "team": row["team"]["name"],
                            "played": row["playedGames"],
                            "won": row["won"],
                            "drawn": row["draw"],
                            "lost": row["lost"],
                            "gf": row["goalsFor"],
                            "ga": row["goalsAgainst"],
                            "gd": row["goalDifference"],
                            "pts": row["points"],
                        }
                        for row in standing.get("table", [])
                    ],
                })
            return groups
        return self._get("standings", fetch)

    def get_matches(self, status: str = "FINISHED") -> list[dict] | None:
        def fetch():
            data = self._fetch(f"/competitions/{FOOTBALL_DATA_COMPETITION_ID}/matches?status={status}")
            if not data:
                return None
            return [
                {
                    "date": m["utcDate"][:10],
                    "stage": m.get("stage", ""),
                    "group": m.get("group"),
                    "home": m["homeTeam"]["name"],
                    "away": m["awayTeam"]["name"],
                    "score": f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}",
                    "status": m["status"],
                }
                for m in data.get("matches", [])
            ]
        key = f"matches_{status}"
        return self._get(key, fetch)

    def get_scorers(self) -> list[dict] | None:
        def fetch():
            data = self._fetch(f"/competitions/{FOOTBALL_DATA_COMPETITION_ID}/scorers?limit=10")
            if not data:
                return None
            return [
                {
                    "player": s["player"]["name"],
                    "team": s["team"]["name"],
                    "goals": s["goals"],
                    "assists": s.get("assists", 0),
                    "penalties": s.get("penalties", 0),
                }
                for s in data.get("scorers", [])
            ]
        return self._get("scorers", fetch)

    def get_squad(self, team_id: int) -> list[dict] | None:
        def fetch():
            data = self._fetch(f"/teams/{team_id}")
            if not data:
                return None
            return [
                {
                    "name": p["name"],
                    "position": p.get("position"),
                    "nationality": p.get("nationality"),
                    "dob": p.get("dateOfBirth", "")[:10],
                }
                for p in data.get("squad", [])
            ]
        return self._get(f"squad_{team_id}", fetch)
