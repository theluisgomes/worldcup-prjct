import httpx
from connectors.base import BaseConnector
from config import API_FOOTBALL_KEY, API_FOOTBALL_LEAGUE_ID, API_FOOTBALL_SEASON, CACHE_TTL

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"


class APIFootballConnector(BaseConnector):
    name = "api_football"
    ttl = CACHE_TTL["sports"]

    def is_configured(self) -> bool:
        return bool(API_FOOTBALL_KEY)

    def _headers(self) -> dict:
        return {
            "X-RapidAPI-Key": API_FOOTBALL_KEY,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
        }

    def _fetch(self, path: str, params: dict = None) -> dict | None:
        r = httpx.get(f"{BASE_URL}/{path}", headers=self._headers(), params=params or {}, timeout=10)
        r.raise_for_status()
        return r.json()

    def get_standings(self) -> list[dict] | None:
        def fetch():
            data = self._fetch("standings", {"league": API_FOOTBALL_LEAGUE_ID, "season": API_FOOTBALL_SEASON})
            standings = data.get("response", [])
            if not standings:
                return None
            groups = []
            for league_data in standings:
                for group in league_data.get("league", {}).get("standings", []):
                    groups.append({
                        "group": group[0].get("group") if group else "N/A",
                        "table": [
                            {
                                "pos": row["rank"],
                                "team": row["team"]["name"],
                                "played": row["all"]["played"],
                                "won": row["all"]["win"],
                                "drawn": row["all"]["draw"],
                                "lost": row["all"]["lose"],
                                "gf": row["all"]["goals"]["for"],
                                "ga": row["all"]["goals"]["against"],
                                "gd": row["goalsDiff"],
                                "pts": row["points"],
                            }
                            for row in group
                        ],
                    })
            return groups
        return self._get("standings", fetch)

    def get_fixtures(self, status: str = "FT") -> list[dict] | None:
        def fetch():
            data = self._fetch("fixtures", {
                "league": API_FOOTBALL_LEAGUE_ID,
                "season": API_FOOTBALL_SEASON,
                "status": status,
            })
            return [
                {
                    "date": f.get("fixture", {}).get("date", "")[:10],
                    "stage": f.get("league", {}).get("round", ""),
                    "home": f.get("teams", {}).get("home", {}).get("name", ""),
                    "away": f.get("teams", {}).get("away", {}).get("name", ""),
                    "score": f"{f.get('goals', {}).get('home', '?')}-{f.get('goals', {}).get('away', '?')}",
                    "status": f.get("fixture", {}).get("status", {}).get("long", ""),
                }
                for f in data.get("response", [])
            ]
        key = f"fixtures_{status}"
        return self._get(key, fetch)

    def get_top_scorers(self) -> list[dict] | None:
        def fetch():
            data = self._fetch("players/topscorers", {
                "league": API_FOOTBALL_LEAGUE_ID,
                "season": API_FOOTBALL_SEASON,
            })
            return [
                {
                    "player": item["player"]["name"],
                    "team": item["statistics"][0]["team"]["name"],
                    "goals": item["statistics"][0]["goals"]["total"] or 0,
                    "assists": item["statistics"][0]["goals"]["assists"] or 0,
                    "shots_on": item["statistics"][0]["shots"]["on"] or 0,
                }
                for item in data.get("response", [])
            ]
        return self._get("top_scorers", fetch)

    def get_squad(self, team_id: int) -> list[dict] | None:
        def fetch():
            data = self._fetch("players/squads", {"team": team_id})
            players = []
            for entry in data.get("response", []):
                for p in entry.get("players", []):
                    players.append({
                        "name": p["name"],
                        "age": p.get("age"),
                        "number": p.get("number"),
                        "position": p.get("position"),
                    })
            return players or None
        return self._get(f"squad_{team_id}", fetch)
