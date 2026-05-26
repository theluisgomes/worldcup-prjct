# Motor Analítico Copa do Mundo

## Visão Geral
Motor de Inferência Analítica e NLI (Natural Language Interface) para dados históricos e diários da Copa do Mundo da FIFA. O sistema transforma consultas em linguagem natural em relatórios estruturados com erro zero de alucinação numérica.

## Estrutura
```
worldcup-prjct/
├── data/
│   ├── historical_data.json      # Dados estáticos 1930–2022 (22 edições)
│   └── cache/                    # Cache TTL automático dos dados ao vivo
├── connectors/
│   ├── base.py                   # Cache TTL + interface base
│   ├── sports/
│   │   ├── football_data.py      # football-data.org (classificação, resultados, escalações)
│   │   └── api_football.py       # API-Football / RapidAPI (stats detalhadas)
│   ├── news/
│   │   ├── rss.py                # BBC, ESPN, Goal.com, AS.com (sem API key)
│   │   └── newsapi.py            # NewsAPI.org (100 req/dia no plano gratuito)
│   └── social/
│       ├── reddit.py             # r/worldcup, r/soccer, r/futebol (sem API key)
│       └── twitter.py            # Twitter/X API v2 (requer Bearer Token)
├── engine/
│   ├── analytical_engine.py      # Claude NLI + prompt caching
│   ├── context_builder.py        # Agrega todas as fontes ao vivo
│   ├── data_loader.py            # Carga do histórico estático
│   └── prompts.py                # System prompt com guardrails e contratos de dados
├── config.py                     # Variáveis de ambiente
├── main.py                       # CLI interativo
├── requirements.txt
└── .env.example                  # Template de chaves de API
```

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# edite .env com suas chaves
python main.py
```

## Fontes de dados e chaves necessárias
| Fonte | Variável de ambiente | Gratuita? |
|---|---|---|
| football-data.org | `FOOTBALL_DATA_API_KEY` | Sim (registro gratuito) |
| API-Football | `API_FOOTBALL_KEY` | Sim (tier limitado no RapidAPI) |
| NewsAPI.org | `NEWSAPI_KEY` | Sim (100 req/dia) |
| RSS (BBC/ESPN/Goal/AS) | — | Sim (sem chave) |
| Reddit | — | Sim (sem chave) |
| Twitter/X | `TWITTER_BEARER_TOKEN` | Não (Basic plan mínimo) |

O sistema opera com qualquer subconjunto configurado — fontes sem chave são omitidas silenciosamente.

## Regras de Negócio
- Escopo restrito a `[HISTORICAL_DATA]`, `[LIVE_SPORTS]`, `[NEWS_BRIEFING]` e `[SOCIAL_SIGNALS]`
- Cálculos via Chain of Thought antes de qualquer output numérico
- Alemanha Ocidental + Alemanha unificadas em consultas históricas gerais
- Tabelas Markdown obrigatórias para 3+ entidades comparadas
- Tom analítico, sem jargões de transmissão esportiva
- Sentimento social sempre rotulado como "percepção pública", não como fato verificado

## Comandos CLI
- `/reset` — limpa histórico da conversa (mantém dados ao vivo carregados)
- `/refresh` — recarrega todos os dados ao vivo (ignora cache)
- `/fontes` — lista status das fontes de dados
- `/sair` — encerra a sessão
