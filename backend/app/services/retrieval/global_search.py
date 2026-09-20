"""
Global search retrieval service — Leiden community report map-reduce synthesis.
"""

from __future__ import annotations

import logging
from typing import Any

from neo4j.exceptions import Neo4jError, ServiceUnavailable
from pydantic import BaseModel, Field

from app.db.neo4j import get_neo4j_driver
from app.llm.client import get_synthesis_model

logger = logging.getLogger(__name__)


class GlobalSearchResult(BaseModel):
    """Holistic document synthesis based on community summaries."""

    query: str
    communities_used: list[dict[str, Any]] = Field(default_factory=list)
    answer: str
    key_findings: list[str] = Field(default_factory=list)


GLOBAL_SEARCH_PROMPT = """You are an academic synthesis specialist.
Synthesize a comprehensive, high-level response to the user query based solely on the community cluster reports provided below.

Community Reports:
{context}

User Query:
{query}

Provide a clear, cohesive answer citing relevant community themes where applicable.
"""


def execute_global_search(
    document_id: str,
    query: str,
) -> GlobalSearchResult:
    """
    Perform global map-reduce search across Leiden community clusters in Neo4j.
    """
    communities: list[dict[str, Any]] = []

    try:
        driver = get_neo4j_driver()
        cypher = """
        MATCH (c:Community {document_id: $doc_id})
        RETURN c.id AS id, c.title AS title, c.summary AS summary,
               c.key_findings AS key_findings, c.rating AS rating
        ORDER BY c.rating DESC
        LIMIT 10
        """
        with driver.session() as session:
            result = session.run(cypher, doc_id=document_id)
            for record in result:
                communities.append(
                    {
                        "id": record["id"],
                        "title": record["title"] or f"Community {record['id']}",
                        "summary": record["summary"] or "",
                        "key_findings": record["key_findings"] or [],
                        "rating": record["rating"] or 8.0,
                    }
                )
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Neo4j community fetch failed for global search: %s", exc)

    all_key_findings: list[str] = []
    for c in communities:
        all_key_findings.extend(c["key_findings"])

    if not communities:
        return GlobalSearchResult(
            query=query,
            communities_used=[],
            answer="No community reports found for this document.",
            key_findings=[],
        )

    # Format context for LLM synthesis
    context_blocks: list[str] = []
    for c in communities:
        findings_str = "\n".join(f"- {f}" for f in c["key_findings"])
        context_blocks.append(
            f"### {c['title']} (Rating: {c['rating']})\n"
            f"Summary: {c['summary']}\n"
            f"Findings:\n{findings_str}"
        )
    formatted_context = "\n\n".join(context_blocks)

    # Invoke LLM for synthesis
    try:
        model = get_synthesis_model()
        prompt_text = GLOBAL_SEARCH_PROMPT.format(
            context=formatted_context,
            query=query,
        )
        response = model.invoke(prompt_text)
        answer = str(response.content)
    except (ValueError, RuntimeError, OSError) as exc:
        logger.warning("Global search LLM synthesis fallback: %s", exc)
        answer = (
            f"High-level synthesis for '{query}':\n\n"
            + "\n\n".join(
                f"**{c['title']}**: {c['summary']}" for c in communities[:3]
            )
        )

    return GlobalSearchResult(
        query=query,
        communities_used=communities,
        answer=answer,
        key_findings=all_key_findings[:10],
    )

