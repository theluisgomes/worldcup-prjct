import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import anthropic
import json

from engine.data_loader import load_historical, format_historical
from engine.context_builder import ContextBuilder
from engine.prompts import SYSTEM_PROMPT

app = FastAPI(title="Motor Analítico Copa do Mundo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

_context_builder = ContextBuilder()
_anthropic = anthropic.Anthropic()
_system_prompt: str | None = None


def _get_system_prompt(force_refresh: bool = False) -> str:
    global _system_prompt
    if _system_prompt is None or force_refresh:
        historical = format_historical(load_historical())
        live_context = _context_builder.build()
        _system_prompt = SYSTEM_PROMPT.format(
            historical_data=historical,
            live_context=live_context,
        )
    return _system_prompt


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    refresh: bool = False


@app.post("/api/chat")
async def chat(req: ChatRequest):
    system = _get_system_prompt(force_refresh=req.refresh)
    messages = req.history + [{"role": "user", "content": req.message}]

    def generate():
        with _anthropic.messages.stream(
            model="claude-opus-4-7",
            max_tokens=2048,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {json.dumps({'delta': text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/status")
async def status():
    from config import (
        FOOTBALL_DATA_API_KEY, API_FOOTBALL_KEY,
        NEWSAPI_KEY, TWITTER_BEARER_TOKEN,
    )
    return {
        "football_data": bool(FOOTBALL_DATA_API_KEY),
        "api_football": bool(API_FOOTBALL_KEY),
        "rss": True,
        "newsapi": bool(NEWSAPI_KEY),
        "reddit": True,
        "twitter": bool(TWITTER_BEARER_TOKEN),
    }
