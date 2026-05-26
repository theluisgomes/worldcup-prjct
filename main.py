#!/usr/bin/env python3
"""CLI interativo — Motor Analítico Copa do Mundo."""

import sys
from engine.analytical_engine import AnalyticalEngine

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║   MOTOR ANALÍTICO — COPA DO MUNDO FIFA                           ║
║   Dados: Histórico (1930–2022) + Live Sports + News + Social     ║
╠══════════════════════════════════════════════════════════════════╣
║   /reset    → limpa histórico da conversa                        ║
║   /refresh  → recarrega dados ao vivo (ignora cache)             ║
║   /fontes   → lista fontes de dados configuradas                 ║
║   /sair     → encerra a sessão                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

SOURCES_INFO = """
Fontes de dados:
  Sports  : football-data.org + API-Football (RapidAPI)
  Notícias: RSS (BBC, ESPN, Goal.com, AS.com) + NewsAPI.org
  Social  : Reddit (r/worldcup, r/soccer, r/futebol) + Twitter/X

Configure as chaves via variáveis de ambiente (ver .env.example).
Fontes sem chave são omitidas silenciosamente — as demais continuam operando.
"""


def main() -> None:
    print(BANNER)
    engine = AnalyticalEngine()

    while True:
        try:
            user_input = input("\nConsulta > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSessão encerrada.")
            sys.exit(0)

        if not user_input:
            continue

        match user_input.lower():
            case "/sair":
                print("Sessão encerrada.")
                sys.exit(0)
            case "/reset":
                engine.reset()
                print("Histórico da conversa limpo.")
            case "/refresh":
                engine.refresh()
                print("Dados ao vivo recarregados.")
            case "/fontes":
                print(SOURCES_INFO)
            case _:
                print()
                try:
                    print(engine.query(user_input))
                except Exception as e:
                    print(f"Erro ao processar consulta: {e}")


if __name__ == "__main__":
    main()
