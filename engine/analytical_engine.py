import anthropic
from .data_loader import load_historical, load_daily_inputs, format_historical, format_daily_inputs
from .prompts import SYSTEM_PROMPT

MODEL = "claude-opus-4-7"


def build_system_prompt() -> str:
    historical = format_historical(load_historical())
    daily = format_daily_inputs(load_daily_inputs())
    return SYSTEM_PROMPT.format(historical_data=historical, daily_inputs=daily)


class AnalyticalEngine:
    def __init__(self):
        self._client = anthropic.Anthropic()
        self._system_prompt = build_system_prompt()
        self._history: list[dict] = []

    def query(self, user_input: str) -> str:
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

        assistant_text = response.content[0].text
        self._history.append({"role": "assistant", "content": assistant_text})
        return assistant_text

    def reset(self):
        self._history.clear()
