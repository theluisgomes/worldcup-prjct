# Motor Analítico Copa do Mundo

## Visão Geral
Motor de Inferência Analítica e NLI (Natural Language Interface) para dados históricos e diários da Copa do Mundo da FIFA. O sistema transforma consultas em linguagem natural em relatórios estruturados com erro zero de alucinação numérica.

## Estrutura
```
worldcup-prjct/
├── data/
│   ├── historical_data.json   # Dados estáticos 1930–2022 (22 edições)
│   └── daily_inputs.json      # Resultados do torneio em andamento
├── engine/
│   ├── analytical_engine.py   # Cliente Anthropic + gerenciamento de contexto
│   ├── data_loader.py         # Carga e formatação dos datasets
│   └── prompts.py             # System prompt com guardrails e contratos de dados
├── main.py                    # CLI interativo
└── requirements.txt
```

## Setup
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...
python main.py
```

## Injetar dados diários
Edite `data/daily_inputs.json` seguindo o schema:
```json
{
  "torneio_atual": "Copa do Mundo 2026",
  "partidas": [
    {
      "data": "2026-06-11",
      "fase": "Fase de Grupos",
      "time_casa": "Brasil",
      "time_visitante": "Alemanha",
      "gols_casa": 2,
      "gols_visitante": 1,
      "status_partida": "Encerrada"
    }
  ]
}
```

## Regras de Negócio (Spec SPEC-DRIVEN)
- Escopo restrito a `[HISTORICAL_DATA]` e `[DAILY_INPUTS]`
- Cálculos via Chain of Thought antes de qualquer output numérico
- Alemanha Ocidental + Alemanha unificadas em consultas históricas gerais
- Tabelas Markdown obrigatórias para 3+ entidades comparadas
- Tom analítico, sem jargões de transmissão esportiva
