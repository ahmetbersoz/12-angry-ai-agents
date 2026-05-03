from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Provider constants
# ---------------------------------------------------------------------------
OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1-nano"]
DEFAULT_OLLAMA_MODELS = [
    "llama3.1",
    "llama3",
    "qwen2.5",
    "mistral",
    "gemma2",
    "phi3",
    "deepseek-r1",
]
OLLAMA_DEFAULT_BASE_URL = "http://localhost:11434/v1"
OPENROUTER_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODELS = [
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
    "anthropic/claude-sonnet-4",
    "anthropic/claude-haiku-4",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "meta-llama/llama-4-maverick",
    "meta-llama/llama-4-scout",
    "deepseek/deepseek-chat-v3",
    "qwen/qwen3-235b-a22b",
]

# model_info for non-OpenAI providers (bypasses AutoGen model name validation)
GENERIC_MODEL_INFO = {
    "vision": False,
    "function_calling": False,
    "json_output": False,
    "family": "unknown",
    "structured_output": False,
}


@dataclass
class Config:
    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "openai"))
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openrouter_api_key: str = field(
        default_factory=lambda: os.getenv("OPENROUTER_API_KEY", "")
    )
    model_name: str = field(default_factory=lambda: os.getenv("MODEL_NAME", "gpt-4o-mini"))
    base_url: str | None = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL"))
    max_turns: int = 150
    turns_between_votes: int = 12
    temperature: float = 0.9
