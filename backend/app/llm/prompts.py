"""
LangChain Prompt Templates and Pydantic Schemas for LLM tasks.

Covers:
1. Research Mode: Entity & Relationship Extraction
2. Study Mode: Structural Chapter/Section/Topic Hierarchy & Conceptual Prerequisites
3. Community Summarization (Leiden clusters)
4. High-Yield Exam Gist Generation
5. Regulus AI Guide Grounded Answer Synthesis
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# ══════════════════════════════════════════════════════════════════════
# 1. Research Mode: Entity & Relationship Extraction Schemas & Prompts
# ══════════════════════════════════════════════════════════════════════


class ExtractedEntity(BaseModel):
    name: str = Field(description="Canonical capitalized name of the entity")
    type: str = Field(
        description="Category: 'CONCEPT', 'PERSON', 'ORGANIZATION', 'LOCATION', 'DATASET', or 'METHOD'"
    )
    description: str = Field(
        description="Comprehensive 1-2 sentence description of the entity's role in this text"
    )


class ExtractedRelationship(BaseModel):
    source: str = Field(
        description="Source entity name (must match an extracted entity)"
    )
    target: str = Field(
        description="Target entity name (must match an extracted entity)"
    )
    relation: str = Field(
        description="Predicate verb/action connecting them (e.g. 'PROPOSES', 'EVALUATES_ON', 'INCORPORATES')"
    )
    description: str = Field(
        description="Explanation of how and why these entities relate in this context"
    )
    weight: float = Field(
        default=1.0, description="Relationship strength/importance (0.0 to 1.0)"
    )


class ExtractionResult(BaseModel):
    entities: list[ExtractedEntity] = Field(default_factory=list)
    relationships: list[ExtractedRelationship] = Field(default_factory=list)


EXTRACTION_SYSTEM_PROMPT = """You are an expert academic knowledge graph engineer.
Your task is to extract primary entities and their semantic relationships from the provided research text.

Entity Guidelines:
- Extract key concepts, authors, institutions, datasets, and methods.
- Canonicalize entity names (e.g. use 'Multi-Head Attention' rather than 'attention layers').
- Discard trivial or overly broad terms (like 'paper', 'data', 'performance').

Relationship Guidelines:
- Connect entities with meaningful, directed academic predicates (e.g. 'OUTPERFORMS', 'REDUCES_LATENCY_OF', 'TRAINED_ON').
- Provide a clear, factual explanation for every relationship based solely on the text.
"""

EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", EXTRACTION_SYSTEM_PROMPT),
        (
            "human",
            "Extract entities and relationships from the following text chunk:\n\n{text}",
        ),
    ]
)

# ══════════════════════════════════════════════════════════════════════
# 2. Study Mode: Structural Hierarchy & Prerequisites
# ══════════════════════════════════════════════════════════════════════


class ExtractedSubtopic(BaseModel):
    name: str = Field(description="Subtopic title")
    summary: str = Field(description="1-2 sentence summary")
    needs_context: bool = Field(
        default=False,
        description="True if this concept requires prerequisites outside this book/chapter",
    )


class ExtractedTopic(BaseModel):
    name: str = Field(description="Core topic title")
    summary: str = Field(description="1-2 sentence core concept explanation")
    subtopics: list[ExtractedSubtopic] = Field(default_factory=list)
    conceptually_links_to: list[str] = Field(
        default_factory=list,
        description="Names of other topics this concept logically builds upon or connects with",
    )


class ExtractedSection(BaseModel):
    title: str = Field(description="Section heading")
    summary: str = Field(description="Overview summary of this section")
    topics: list[ExtractedTopic] = Field(default_factory=list)


class ExtractedChapter(BaseModel):
    title: str = Field(description="Chapter title")
    chapter_number: int | None = Field(default=None)
    sections: list[ExtractedSection] = Field(default_factory=list)


class StudyHierarchyResult(BaseModel):
    chapters: list[ExtractedChapter] = Field(default_factory=list)


STUDY_HIERARCHY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a textbook curriculum specialist. Structure textbook content into a clear "
                "pedagogical hierarchy: Chapter -> Section -> Topic -> Subtopic. Identify conceptual prerequisites "
                "and mark `needs_context=True` when a concept assumes prior knowledge not covered here."
            ),
        ),
        (
            "human",
            "Parse the following textbook excerpt into its structured curriculum hierarchy:\n\n{text}",
        ),
    ]
)

# ══════════════════════════════════════════════════════════════════════
# 3. Community Summarization (Leiden clusters)
# ══════════════════════════════════════════════════════════════════════


class CommunitySummaryResult(BaseModel):
    title: str = Field(
        description="A concise thematic title for this community of concepts"
    )
    summary: str = Field(
        description="Executive multi-paragraph synthesis of the community's theme"
    )
    key_findings: list[str] = Field(
        description="Bullet points of the main scientific/pedagogical takeaways"
    )
    rating: float = Field(
        default=8.0,
        description="Overall significance of this cluster to the document (1.0 to 10.0)",
    )


COMMUNITY_SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a synthesis specialist. You are given a tightly knit community cluster of entities "
                "and relationships extracted from academic literature. Synthesize them into an overarching thematic summary."
            ),
        ),
        (
            "human",
            "Synthesize this community of concepts:\n\n{entities_and_relationships}",
        ),
    ]
)

# ══════════════════════════════════════════════════════════════════════
# 4. High-Yield Exam Gist
# ══════════════════════════════════════════════════════════════════════


class ExamGistResult(BaseModel):
    top_concepts: list[str] = Field(
        description="Top 3-5 high-yield concepts most likely to be tested"
    )
    key_formulas: list[str] = Field(
        description="Essential mathematical formulas or definitions to memorize"
    )
    common_pitfalls: list[str] = Field(
        description="Common exam traps, misconceptions, or edge cases"
    )
    likely_questions: list[str] = Field(
        description="3-5 potential exam questions with brief solution hints"
    )


EXAM_GIST_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a top-tier academic exam tutor. Your goal is to synthesize academic material into a "
                "dense, high-yield '2-Minute Exam Gist' designed for rapid revision before exams."
            ),
        ),
        (
            "human",
            "Generate an exam revision gist from the following core topics and concepts:\n\n{text}",
        ),
    ]
)

# ══════════════════════════════════════════════════════════════════════
# 5. Regulus AI Guide Answer Synthesis
# ══════════════════════════════════════════════════════════════════════

REGULUS_SYSTEM_PROMPT = """You are Regulus, an intelligent, neutral academic knowledge guide for Untangle.
Your mission is to answer user queries with grounded precision based on the provided Knowledge Graph context and source text chunks.

Guidelines:
1. Always cite exact chunks when stating facts, e.g. [Chunk 3].
2. Refer to entities and relationships by their exact graph names.
3. Be clear, analytical, and concise. Do not use game jargon or flowery filler words.
4. If outside context is required, explicitly point out prerequisite topics that need context.
"""

REGULUS_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", REGULUS_SYSTEM_PROMPT),
        (
            "human",
            (
                "Context from Knowledge Graph Subgraph:\n{subgraph_context}\n\n"
                "Verbatim Chunks:\n{chunks_context}\n\n"
                "Question: {question}"
            ),
        ),
    ]
)
