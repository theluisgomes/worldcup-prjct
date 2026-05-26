#!/usr/bin/env python3
"""CLI interativo para o Motor Analítico Copa do Mundo."""

import sys
from engine.analytical_engine import AnalyticalEngine

BANNER = """
╔══════════════════════════════════════════════════════════╗
║   MOTOR ANALÍTICO — COPA DO MUNDO FIFA (1930–2022)       ║
║   Comandos: /reset  → limpa histórico  |  /sair → encerra ║
╚══════════════════════════════════════════════════════════╝
"""


def main():
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
        if user_input.lower() == "/sair":
            print("Sessão encerrada.")
            sys.exit(0)
        if user_input.lower() == "/reset":
            engine.reset()
            print("Histórico da conversa limpo.")
            continue

        print()
        try:
            response = engine.query(user_input)
            print(response)
        except Exception as e:
            print(f"Erro ao processar consulta: {e}")


if __name__ == "__main__":
    main()
