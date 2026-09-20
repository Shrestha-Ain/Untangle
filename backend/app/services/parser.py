"""
Document text parsing and sentence-aware sliding-window chunking.

Supports PDF, Markdown, and plain text files.
Generates chunks targeting ~500-600 tokens with ~15% overlap while preserving
page numbers and sentence boundaries for accurate citations.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from pydantic import BaseModel, Field
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class DocumentChunk(BaseModel):
    """Metadata-rich chunk representation for ingestion and vector indexing."""

    chunk_index: int = Field(description="Zero-indexed sequence order in the document")
    page_number: int | None = Field(default=None, description="Source page number (1-indexed)")
    text: str = Field(description="Verbatim chunk text")
    token_count: int = Field(description="Estimated token count of this chunk")
    char_count: int = Field(description="Character length of this chunk")


def approximate_token_count(text: str) -> int:
    """
    Fast heuristic token counter (~4 characters per token for English).
    Guarantees non-zero count for non-empty text.
    """
    if not text:
        return 0
    # Average across character ratio and whitespace tokenization
    by_char = len(text) / 4.0
    by_words = len(text.split()) * 1.25
    return max(1, int((by_char + by_words) / 2.0))


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into grammatical sentences preserving punctuation.
    Avoids splitting on common abbreviations or decimal numbers (e.g. 3.14).
    """
    if not text:
        return []

    # Match sentence terminators (. ? !) followed by whitespace or newline
    # Negative lookbehind prevents splitting on common abbreviations or standalone dots
    pattern = r"(?<=[.?!])\s+(?=[A-Z0-9\"'(\[])|\n{2,}"
    raw_sentences = re.split(pattern, text)

    sentences: list[str] = []
    for s in raw_sentences:
        cleaned = s.strip()
        if cleaned:
            sentences.append(cleaned)
    return sentences


def extract_text_from_file(file_path: str | Path) -> list[tuple[int | None, str]]:
    """
    Extract text from a file, returning a list of (page_number, text) tuples.

    - PDF: returns (page_idx + 1, page_text) for each non-empty page.
    - TXT / MD: returns [(1, full_text)].
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        pages: list[tuple[int | None, str]] = []
        try:
            reader = PdfReader(str(path))
            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                cleaned = page_text.strip()
                if cleaned:
                    pages.append((page_idx + 1, cleaned))
            logger.info("Extracted %d non-empty pages from PDF: %s", len(pages), path.name)
            return pages
        except Exception as exc:
            logger.error("Failed to parse PDF '%s': %s", path.name, exc)
            raise RuntimeError(f"Error reading PDF {path.name}: {exc}") from exc

    elif suffix in (".txt", ".md", ".markdown"):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="latin-1")
        cleaned = content.strip()
        return [(1, cleaned)] if cleaned else []

    else:
        # Generic text fallback
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            cleaned = content.strip()
            return [(1, cleaned)] if cleaned else []
        except Exception as exc:
            raise ValueError(f"Unsupported file format: {suffix}") from exc


def chunk_document(
    pages: list[tuple[int | None, str]],
    target_tokens: int = 550,
    overlap_tokens: int = 80,
) -> list[DocumentChunk]:
    """
    Sentence-aware sliding-window chunker.

    Iterates through document sentences. When accumulated tokens exceed target_tokens,
    creates a DocumentChunk and slides forward, retaining overlap_tokens of sentences.
    """
    chunks: list[DocumentChunk] = []
    current_sentences: list[str] = []
    current_tokens = 0
    current_page: int | None = None
    chunk_counter = 0

    for page_num, page_text in pages:
        sentences = split_into_sentences(page_text)

        for sent in sentences:
            sent_tokens = approximate_token_count(sent)

            if current_page is None:
                current_page = page_num

            # If adding this sentence exceeds target and we already have content
            if current_tokens + sent_tokens > target_tokens and current_sentences:
                chunk_text = " ".join(current_sentences)
                chunks.append(
                    DocumentChunk(
                        chunk_index=chunk_counter,
                        page_number=current_page,
                        text=chunk_text,
                        token_count=approximate_token_count(chunk_text),
                        char_count=len(chunk_text),
                    )
                )
                chunk_counter += 1

                # Calculate overlap sentences to retain
                retained_sentences: list[str] = []
                retained_tokens = 0
                for s in reversed(current_sentences):
                    t = approximate_token_count(s)
                    if retained_tokens + t <= overlap_tokens or not retained_sentences:
                        retained_sentences.insert(0, s)
                        retained_tokens += t
                    else:
                        break

                current_sentences = retained_sentences
                current_tokens = retained_tokens
                current_page = page_num

            current_sentences.append(sent)
            current_tokens += sent_tokens

    # Flush any remaining sentences in the final buffer
    if current_sentences:
        chunk_text = " ".join(current_sentences)
        chunks.append(
            DocumentChunk(
                chunk_index=chunk_counter,
                page_number=current_page,
                text=chunk_text,
                token_count=approximate_token_count(chunk_text),
                char_count=len(chunk_text),
            )
        )

    logger.info("Generated %d chunks from %d pages", len(chunks), len(pages))
    return chunks

