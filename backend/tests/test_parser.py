"""
Unit tests for Document Parser and Sentence-Aware Chunker.
"""

from pypdf import PdfWriter

from app.services.parser import (
    approximate_token_count,
    chunk_document,
    extract_text_from_file,
    split_into_sentences,
)


def test_approximate_token_count():
    """Verify fast heuristic token counter."""
    assert approximate_token_count("") == 0
    assert approximate_token_count("Hello world") >= 2
    # 400 chars of text should be ~80-120 tokens
    text = "The Transformer architecture relies entirely on an attention mechanism to draw global dependencies. " * 4
    count = approximate_token_count(text)
    assert 60 <= count <= 140


def test_split_into_sentences():
    """Verify sentence splitting respects periods, abbreviations, and newlines."""
    text = "Scaled Dot-Product Attention uses Q and K. The scaling factor is sqrt(d_k) = 8.0! Does it prevent vanishing gradients? Yes, it does."
    sentences = split_into_sentences(text)
    assert len(sentences) == 4
    assert sentences[0] == "Scaled Dot-Product Attention uses Q and K."
    assert "8.0!" in sentences[1]
    assert sentences[2] == "Does it prevent vanishing gradients?"
    assert sentences[3] == "Yes, it does."


def test_extract_text_from_text_and_markdown(tmp_path):
    """Verify reading plain text and markdown files."""
    md_file = tmp_path / "sample.md"
    md_file.write_text("# Chapter 1: Introduction\n\nThis is a test of the markdown parser.", encoding="utf-8")

    pages = extract_text_from_file(md_file)
    assert len(pages) == 1
    assert pages[0][0] == 1
    assert "Chapter 1: Introduction" in pages[0][1]


def test_extract_text_from_pdf(tmp_path):
    """Verify reading PDF pages and extracting text."""
    pdf_path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(str(pdf_path))

    # Blank page returns 0 non-empty pages
    pages = extract_text_from_file(pdf_path)
    assert len(pages) == 0


def test_chunk_document_sliding_window():
    """Verify chunk generation, target token limits, and sentence overlap."""
    sentences = [
        f"Sentence number {i} provides detailed discussion of attention sublayers."
        for i in range(1, 40)
    ]
    full_text = " ".join(sentences)
    pages = [(1, full_text)]

    chunks = chunk_document(pages, target_tokens=100, overlap_tokens=30)
    assert len(chunks) > 1

    # Verify chunk sequence and structure
    for i, c in enumerate(chunks):
        assert c.chunk_index == i
        assert c.page_number == 1
        assert c.token_count > 0
        assert len(c.text) > 0

    # Verify overlap: subsequent chunk contains the last sentence of the previous chunk
    first_chunk_text = chunks[0].text
    second_chunk_text = chunks[1].text
    last_sent_first = first_chunk_text.split(".")[-2].strip() + "."
    assert last_sent_first in second_chunk_text

