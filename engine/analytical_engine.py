import anthropic
from engine.data_loader import load_historical, format_historical
from engine.context_builder import ContextBuilder
from engine.prompts import SYSTEM_PROMPT

MODEL = "claude-opus-4-7"


def _build_system_prompt(live_context: str) -> str:
    historical = format_historical(load_historical())
    return SYSTEM_PROMPT.format(historical_data=historical, live_context=live_context)


class AnalyticalEngine:
    def __init__(self):
        self._client = anthropic.Anthropic()
        self._builder = ContextBuilder()
        self._history: list[dict] = []
        self._system_prompt: str | None = None

    def _ensure_system_prompt(self) -> None:
        if self._system_prompt is None:
            print("Carregando dados ao vivo...", flush=True)
            live_context = self._builder.build()
            self._system_prompt = _build_system_prompt(live_context)

    def refresh(self) -> None:
        """Força recarregamento dos dados ao vivo (ignora cache)."""
        self._system_prompt = None
        self._ensure_system_prompt()

    def query(self, user_input: str) -> str:
        self._ensure_system_prompt()
        self._history.append({"role": "user", "content": user_input})

        response = self._client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=[
                {
                    "type": "text",
                    "text": self._system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=self._history,
        )

        text = response.content[0].text
        self._history.append({"role": "assistant", "content": text})
        return text

    def reset(self) -> None:
        self._history.clear()
