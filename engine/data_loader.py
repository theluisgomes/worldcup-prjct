import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_historical() -> list[dict]:
    with open(DATA_DIR / "historical_data.json", encoding="utf-8") as f:
        return json.load(f)


def format_historical(data: list[dict]) -> str:
    lines = [
        "Edição | Sede | Campeão | Vice | Equipes | Partidas | Gols | Média/Jogo | Artilheiro | Gols | Placar Final",
        "---|---|---|---|---|---|---|---|---|---|---",
    ]
    for e in data:
        obs = f" ⚠ {e['observacao']}" if e.get("observacao") else ""
        lines.append(
            f"{e['ano']} | {e['sede']} | **{e['campeao']}** | {e['vice']} | "
            f"{e['equipes']} | {e['partidas']} | {e['gols_marcados']} | "
            f"{e['media_gols']:.2f} | {e['artilheiro']} | {e['gols_artilheiro']} | "
            f"{e['placar_final']}{obs}"
        )
    return "\n".join(lines)
