import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_historical() -> list[dict]:
    with open(DATA_DIR / "historical_data.json", encoding="utf-8") as f:
        return json.load(f)


def load_daily_inputs() -> dict:
    with open(DATA_DIR / "daily_inputs.json", encoding="utf-8") as f:
        return json.load(f)


def format_historical(data: list[dict]) -> str:
    lines = ["Edição | Sede | Campeão | Vice | Equipes | Partidas | Gols | Média/Jogo | Artilheiro | Gols | Placar Final"]
    lines.append("---|---|---|---|---|---|---|---|---|---|---")
    for e in data:
        lines.append(
            f"{e['ano']} | {e['sede']} | {e['campeao']} | {e['vice']} | "
            f"{e['equipes']} | {e['partidas']} | {e['gols_marcados']} | "
            f"{e['media_gols']:.2f} | {e['artilheiro']} | {e['gols_artilheiro']} | "
            f"{e['placar_final']}"
        )
    return "\n".join(lines)


def format_daily_inputs(data: dict) -> str:
    if not data.get("torneio_atual") and not data.get("partidas"):
        return "Nenhum dado de torneio em andamento disponível."

    lines = [f"Torneio: {data.get('torneio_atual', 'N/A')}", ""]
    if data.get("partidas"):
        lines.append("Data | Fase | Casa | Visitante | Placar | Status")
        lines.append("---|---|---|---|---|---")
        for p in data["partidas"]:
            placar = f"{p.get('gols_casa', '?')}-{p.get('gols_visitante', '?')}"
            lines.append(
                f"{p.get('data', 'N/A')} | {p.get('fase', 'N/A')} | "
                f"{p.get('time_casa', 'N/A')} | {p.get('time_visitante', 'N/A')} | "
                f"{placar} | {p.get('status_partida', 'N/A')}"
            )
    else:
        lines.append("Sem partidas registradas.")
    return "\n".join(lines)
