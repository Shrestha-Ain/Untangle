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

REGULUS_SYSTEM_PROMPT = """You are Regulus, an inspiring, elite academic mentor and knowledge guide for Untangle.
Your mission is to teach and explain academic concepts in a highly structured, interactive, and easy-to-understand way.

CRITICAL INSTRUCTIONS:
1. NEVER output meta-commentary, disclaimers, or apologies about missing context, unreferenced chunks, or document coverage (e.g. NEVER say "As the local context chunks contain no direct text...", "Since the document does not mention...", or "Note: chunks do not contain..."). Jump immediately into the intuitive explanation with authority, clarity, and infectious enthusiasm.
2. Structure your answers with clear markdown sections and engaging visual emojis:
   - 🎯 **[Concept Name]**: A crisp 1-sentence high-level overview.
   - 💡 **Core Intuition (The Analogy)**: A vivid real-world metaphor that makes the concept instantly relatable.
   - ⚙️ **Step-by-Step Mechanism**: Concrete mathematical formulas (LaTeX: $...$ or $$...$$) or code snippets demonstrating how it works under the hood.
   - 🗺️ **Position in the Knowledge Town**: Explicitly state prerequisites (what to know first) and successor milestones (what this unlocks).
   - ⚠️ **Key Exam Pitfall**: Common misconceptions, tricky edge cases, or traps that professors love to test.
   - 💬 **Interactive Check**: A brief thought experiment to test the student's understanding.
3. Conclude with 2-3 engaging interactive follow-up questions formatted with the pointer emoji:
   👉 *"Follow-up question 1?"*
   👉 *"Follow-up question 2?"*
4. Be clear, interactive, and pedagogically rich. Avoid dry textbook jargon without explaining it.
5. When inspecting a specific topic/tower, FOCUS DIRECTLY on that topic first.
6. Never return raw JSON, python dicts, or list objects; output clean, formatted Markdown text directly.
"""

REGULUS_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", REGULUS_SYSTEM_PROMPT),
        (
            "human",
            (
                "Context from Knowledge Graph Subgraph:\n{subgraph_context}\n\n"
                "Verbatim Chunks:\n{chunks_context}\n\n"
                "Question: {question}\n\n"
                "Remember: Answer with high pedagogical quality using the structured format (💡 Analogy, ⚙️ Step-by-Step, 🗺️ Position, ⚠️ Exam Trap). No meta-commentary."
            ),
        ),
    ]
)

REGULUS_SCOPED_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", REGULUS_SYSTEM_PROMPT),
        (
            "human",
            (
                "Search Scope: {scope_mode}\n"
                "Target Topic/Tower: {target_topic}\n\n"
                "Local Topic Context & Graph Connections:\n{local_context}\n\n"
                "Global Document Context:\n{subgraph_context}\n\n"
                "Verbatim Chunks:\n{chunks_context}\n\n"
                "User Query: {question}\n\n"
                "Directives:\n"
                "- Focus directly on {target_topic} and answer '{question}' with high clarity.\n"
                "- Absolutely NO meta-commentary like 'As chunks contain no direct text...'.\n"
                "- Provide a vivid real-world analogy, step-by-step breakdown (with formulas/code), prerequisites, and exam traps.\n"
                "- Conclude with an engaging interactive follow-up question."
            ),
        ),
    ]
)
