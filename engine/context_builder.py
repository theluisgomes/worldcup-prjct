from connectors.sports.football_data import FootballDataConnector
from connectors.sports.api_football import APIFootballConnector
from connectors.news.rss import RSSConnector
from connectors.news.newsapi import NewsAPIConnector
from connectors.social.reddit import RedditConnector
from connectors.social.twitter import TwitterConnector


class ContextBuilder:
    def __init__(self):
        self._fd = FootballDataConnector()
        self._af = APIFootballConnector()
        self._rss = RSSConnector()
        self._newsapi = NewsAPIConnector()
        self._reddit = RedditConnector()
        self._twitter = TwitterConnector()

    def build(self) -> str:
        sections = []

        sports = self._build_sports()
        if sports:
            sections.append(sports)

        news = self._build_news()
        if news:
            sections.append(news)

        social = self._build_social()
        if social:
            sections.append(social)

        if not sections:
            return "[LIVE_DATA]\nNenhuma fonte de dados ao vivo está configurada no momento."

        return "\n\n---\n\n".join(sections)

    # ── Sports ────────────────────────────────────────────────────────────────

    def _build_sports(self) -> str | None:
        blocks = []

        standings = self._fd.get_standings() or self._af.get_standings()
        if standings:
            blocks.append(self._fmt_standings(standings))

        results = self._fd.get_matches("FINISHED") or self._af.get_fixtures("FT")
        if results:
            blocks.append(self._fmt_matches(results, "Resultados Recentes"))

        scheduled = self._fd.get_matches("SCHEDULED") or self._af.get_fixtures("NS")
        if scheduled:
            blocks.append(self._fmt_matches(scheduled[:8], "Próximas Partidas"))

        scorers = self._fd.get_scorers() or self._af.get_top_scorers()
        if scorers:
            blocks.append(self._fmt_scorers(scorers))

        if not blocks:
            return None
        return "[LIVE_SPORTS]\n\n" + "\n\n".join(blocks)

    def _fmt_standings(self, groups: list) -> str:
        lines = ["### Classificação"]
        for g in groups:
            lines.append(f"\n**{g.get('group', 'Grupo')}**\n")
            lines.append("Pos | Time | J | V | E | D | GP | GC | SG | Pts")
            lines.append("---|---|---|---|---|---|---|---|---|---")
            for r in g.get("table", []):
                lines.append(
                    f"{r['pos']} | {r['team']} | {r['played']} | {r['won']} | "
                    f"{r['drawn']} | {r['lost']} | {r['gf']} | {r['ga']} | "
                    f"{r['gd']:+d} | **{r['pts']}**"
                )
        return "\n".join(lines)

    def _fmt_matches(self, matches: list, title: str) -> str:
        lines = [f"### {title}"]
        lines.append("\nData | Fase | Casa | Placar | Visitante")
        lines.append("---|---|---|---|---")
        for m in matches[-15:]:
            lines.append(
                f"{m.get('date', '')} | {m.get('stage', m.get('round', ''))} | "
                f"{m.get('home', '')} | **{m.get('score', '?-?')}** | {m.get('away', '')}"
            )
        return "\n".join(lines)

    def _fmt_scorers(self, scorers: list) -> str:
        lines = ["### Artilharia"]
        lines.append("\nPos | Jogador | Seleção | Gols | Assistências")
        lines.append("---|---|---|---|---")
        for i, s in enumerate(scorers[:10], 1):
            lines.append(
                f"{i} | {s['player']} | {s['team']} | **{s['goals']}** | "
                f"{s.get('assists', s.get('assists', 0))}"
            )
        return "\n".join(lines)

    # ── News ──────────────────────────────────────────────────────────────────

    def _build_news(self) -> str | None:
        items = []

        rss = self._rss.get_headlines()
        if rss:
            items.extend(rss)

        wc_news = self._newsapi.get_headlines("FIFA World Cup 2026")
        if wc_news:
            items.extend(wc_news)

        if not items:
            return None

        lines = ["[NEWS_BRIEFING]\n"]
        for item in items[:20]:
            source = item.get("source", "")
            title = item.get("title", "")
            summary = item.get("summary") or item.get("description", "")
            published = item.get("published", item.get("published", ""))[:16]
            lines.append(f"**[{source}]** {title}")
            if summary:
                lines.append(f"> {summary}")
            if published:
                lines.append(f"_{published}_")
            lines.append("")
        return "\n".join(lines)

    # ── Social ────────────────────────────────────────────────────────────────

    def _build_social(self) -> str | None:
        blocks = []

        reddit_posts = self._reddit.get_hot_posts()
        if reddit_posts:
            lines = ["### Reddit — Posts em Alta (r/worldcup · r/soccer · r/futebol)"]
            lines.append("\nScore | Comentários | Título | Subreddit")
            lines.append("---|---|---|---")
            for p in reddit_posts[:15]:
                lines.append(
                    f"{p['score']:,} | {p['comments']:,} | {p['title'][:80]} | r/{p['subreddit']}"
                )
            blocks.append("\n".join(lines))

        tweets = self._twitter.get_trending_worldcup()
        if tweets:
            lines = ["### Twitter/X — Menções Recentes (#WorldCup2026)"]
            lines.append("\nLikes | RTs | Texto")
            lines.append("---|---|---")
            for t in sorted(tweets, key=lambda x: x["likes"], reverse=True)[:10]:
                text = t["text"].replace("\n", " ")[:100]
                lines.append(f"{t['likes']:,} | {t['retweets']:,} | {text}")
            blocks.append("\n".join(lines))

        if not blocks:
            return None
        return "[SOCIAL_SIGNALS]\n\n" + "\n\n".join(blocks)
