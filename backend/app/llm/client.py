"""
Model-agnostic LLM client provider using LangChain.

Abstracts model instantiation and provider routing so any model can be swapped
via environment variables without touching business logic.
Provides automatic multi-provider fallbacks on 429 rate limits or provider downtime.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def infer_provider(model_name: str) -> str:
    """Infer LLM provider from model naming convention."""
    model_lower = model_name.lower()
    if model_lower.startswith("gemini"):
        return "google"
    elif any(
        model_lower.startswith(prefix)
        for prefix in ("llama", "mixtral", "gemma", "qwen", "whisper")
    ):
        return "groq"
    elif model_lower.startswith("claude"):
        return "anthropic"
    elif model_lower.startswith(("gpt", "o1", "o3")):
        return "openai"
    return "google"


def create_chat_model(
    model: str,
    provider: str | None = None,
    temperature: float = 0.0,
    streaming: bool = False,
    **kwargs: Any,
) -> BaseChatModel:
    """
    Factory function instantiating a LangChain BaseChatModel for the specified provider.

    Supports Google GenAI (Gemini), Groq (Llama), Anthropic (Claude), and OpenAI.
    """
    settings = get_settings()
    resolved_provider = (provider or infer_provider(model)).lower()

    logger.debug(
        "Instantiating ChatModel: model='%s', provider='%s', temp=%.2f, streaming=%s",
        model,
        resolved_provider,
        temperature,
        streaming,
    )

    if resolved_provider in ("google", "google-genai"):
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = settings.gemini_api_key or "placeholder_gemini_key"
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=temperature,
            **kwargs,
        )

    elif resolved_provider == "groq":
        from langchain_groq import ChatGroq

        api_key = settings.groq_api_key or "gsk_placeholder_groq_key"
        return ChatGroq(
            model=model,
            groq_api_key=api_key,
            temperature=temperature,
            streaming=streaming,
            **kwargs,
        )

    elif resolved_provider == "anthropic":
        try:
            from langchain_anthropic import (
                ChatAnthropic,  # type: ignore[import-not-found]
            )

            api_key = settings.anthropic_api_key or None
            return ChatAnthropic(
                model=model,
                anthropic_api_key=api_key,
                temperature=temperature,
                streaming=streaming,
                **kwargs,
            )
        except ImportError as exc:
            raise RuntimeError(
                "langchain-anthropic is required to use Anthropic models. Install it with `uv add langchain-anthropic`."
            ) from exc

    elif resolved_provider == "openai":
        try:
            from langchain_openai import ChatOpenAI  # type: ignore[import-not-found]

            api_key = settings.openai_api_key or None
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                temperature=temperature,
                streaming=streaming,
                **kwargs,
            )
        except ImportError as exc:
            raise RuntimeError(
                "langchain-openai is required to use OpenAI models. Install it with `uv add langchain-openai`."
            ) from exc

    else:
        raise ValueError(f"Unsupported LLM provider: '{resolved_provider}'")


def get_extraction_model(temperature: float = 0.0) -> BaseChatModel:
    """
    Returns the extraction workhorse model with automatic fallback.

    Primary: settings.extraction_model (e.g. gemini-3.5-flash-lite)
    Fallback: settings.extraction_model_fallback (e.g. gemini-2.5-flash-lite)
    """
    settings = get_settings()
    primary = create_chat_model(
        model=settings.extraction_model,
        temperature=temperature,
    )

    if (
        settings.extraction_model_fallback
        and settings.extraction_model_fallback != settings.extraction_model
    ):
        fallback = create_chat_model(
            model=settings.extraction_model_fallback,
            temperature=temperature,
        )
        return primary.with_fallbacks([fallback])

    return primary


def get_synthesis_model(temperature: float = 0.2) -> BaseChatModel:
    """
    Returns the synthesis model for community summaries and high-yield exam gists.

    Primary: settings.synthesis_model (e.g. gemini-3.5-flash)
    Fallback: settings.synthesis_model_fallback (e.g. llama-3.3-70b-versatile via Groq)
    """
    settings = get_settings()
    primary = create_chat_model(
        model=settings.synthesis_model,
        temperature=temperature,
    )

    if (
        settings.synthesis_model_fallback
        and settings.synthesis_model_fallback != settings.synthesis_model
    ):
        fallback = create_chat_model(
            model=settings.synthesis_model_fallback,
            temperature=temperature,
        )
        return primary.with_fallbacks([fallback])

    return primary


def get_chat_model(temperature: float = 0.3) -> BaseChatModel:
    """
    Returns the low-latency streaming chat model for Regulus AI Guide.

    Primary: settings.chat_model (e.g. llama-3.3-70b-versatile via Groq for <150ms TTFT)
    Fallback: settings.chat_model_fallback (e.g. gemini-3.5-flash streaming)
    """
    settings = get_settings()
    primary = create_chat_model(
        model=settings.chat_model,
        temperature=temperature,
        streaming=True,
    )

    if (
        settings.chat_model_fallback
        and settings.chat_model_fallback != settings.chat_model
    ):
        fallback = create_chat_model(
            model=settings.chat_model_fallback,
            temperature=temperature,
            streaming=True,
        )
        return primary.with_fallbacks([fallback])

    return primary
