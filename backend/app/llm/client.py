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


def clean_llm_text(content: Any) -> str:
    """
    Extracts clean, human-readable plaintext Markdown from LangChain AIMessage content,
    which can be a string, a list of dicts [{'type': 'text', 'text': ...}],
    or a serialized string representation of content blocks.
    Strips raw code wrappers, unescapes newlines, and eliminates robotic disclaimers.
    """
    if not content:
        return ""

    import ast
    import json
    import re

    text = ""
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                parts.append(part.get("text", ""))
            elif hasattr(part, "text"):
                parts.append(getattr(part, "text", ""))
            else:
                parts.append(str(part))
        text = "".join(parts)
    elif isinstance(content, dict):
        text = content.get("text") or content.get("content") or str(content)
    else:
        text = str(content)

    cleaned = text.strip()

    # Case A: Stringified list or dict representation e.g. "[{'type': 'text', 'text': ...}]"
    prefix_match = re.match(r"^\[\s*\{\s*['\"]type['\"]\s*:\s*['\"]text['\"]\s*,\s*['\"]text['\"]\s*:\s*(['\"])", cleaned)
    if prefix_match:
        quote_char = prefix_match.group(1)
        cleaned = cleaned[prefix_match.end():]
        cleaned = re.sub(rf"\{quote_char}\s*\}}?\s*\]?$", "", cleaned).strip()
    elif (
        (cleaned.startswith("[") and ("'type'" in cleaned or '"type"' in cleaned))
        or (cleaned.startswith("{") and ("'text'" in cleaned or '"text"' in cleaned))
    ):
        extracted = None

        # 1. Try json.loads
        try:
            parsed_json = json.loads(cleaned)
            if isinstance(parsed_json, list):
                extracted = "".join(p.get("text", "") for p in parsed_json if isinstance(p, dict))
            elif isinstance(parsed_json, dict):
                extracted = parsed_json.get("text", "")
        except Exception:
            pass

        # 2. Try ast.literal_eval
        if not extracted:
            try:
                parsed_ast = ast.literal_eval(cleaned)
                if isinstance(parsed_ast, list):
                    extracted = "".join(p.get("text", "") for p in parsed_ast if isinstance(p, dict))
                elif isinstance(parsed_ast, dict):
                    extracted = parsed_ast.get("text", "")
            except Exception:
                pass

        # 3. Robust regex extraction with DOTALL
        if not extracted:
            m = re.search(r"['\"]text['\"]\s*:\s*(['\"])(.*?)\1(?:\s*\}|\s*\]|$)", cleaned, re.DOTALL)
            if m:
                extracted = m.group(2)

        # 4. Fallback slicing
        if not extracted:
            # Strip leading wrapper pattern
            cleaned_sub = re.sub(r"^\[\s*\{\s*['\"]type['\"]\s*:\s*['\"]text['\"]\s*,\s*['\"]text['\"]\s*:\s*['\"]", "", cleaned)
            cleaned_sub = re.sub(r"['\"]\s*\}\s*\]$", "", cleaned_sub)
            if cleaned_sub != cleaned:
                extracted = cleaned_sub

        if extracted:
            cleaned = extracted.strip()

    # Unescape literal backslash-escaped characters (e.g. \n, \", \', \t)
    if "\\n" in cleaned:
        cleaned = cleaned.replace("\\n", "\n")
    if "\\\"" in cleaned:
        cleaned = cleaned.replace('\\"', '"')
    if "\\\'" in cleaned:
        cleaned = cleaned.replace("\\'", "'")
    if "\\t" in cleaned:
        cleaned = cleaned.replace("\\t", "  ")

    # Remove apologetic robotic preambles
    cleaned = re.sub(
        r"^(?:(?:As|Since|Although|Because|Note:?)\s+(?:the\s+)?(?:local\s+)?(?:context\s+)?(?:chunks?|text|document|excerpts?|passages?)[^\n]*(?:contain\s+no|do\s+not\s+contain|does\s+not\s+contain|no\s+direct|not\s+found)[^\n]*\n*)+",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = re.sub(
        r"^(?:As an AI language model[^\n]*\n*|Based on general knowledge since[^\n]*\n*|Note:\s*Local context chunks?[^\n]*\n*)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()

    # Remove leading horizontal rules or blank lines left behind after removing preambles
    cleaned = re.sub(r"^(?:(?:\s*---|\s*\*\*\*|\s*___)\s*\n*)+", "", cleaned).strip()

    return cleaned


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


def get_chat_model(
    temperature: float = 0.3,
    model_name: str | None = None,
) -> BaseChatModel:
    """
    Returns the low-latency chat model for Regulus AI Guide.
    Supports user selection between 'flash' and 'sonnet' models.
    """
    settings = get_settings()

    target_model = settings.chat_model
    fallback_model = settings.chat_model_fallback

    if model_name:
        name_lower = model_name.lower()
        if "sonnet" in name_lower or "claude" in name_lower:
            target_model = "claude-3-5-sonnet-20241022" if settings.anthropic_api_key else settings.chat_model
            fallback_model = settings.chat_model
        elif "flash" in name_lower:
            target_model = "gemini-3.5-flash" if settings.gemini_api_key else settings.chat_model
            fallback_model = settings.chat_model

    primary = create_chat_model(
        model=target_model,
        temperature=temperature,
        streaming=True,
    )

    if fallback_model and fallback_model != target_model:
        fallback = create_chat_model(
            model=fallback_model,
            temperature=temperature,
            streaming=True,
        )
        return primary.with_fallbacks([fallback])

    return primary
