"""
Pydantic schemas for Graph API and Retrieval responses.

Covers:
- Knowledge Town graphs (nodes, edges, communities)
- Study Mode hierarchical maps (Chapter -> Section -> Topic -> Subtopic)
- Community clusters
- Deep-dive entity/topic dossiers
- Ordered pedagogical learning paths
- 2-minute high-yield exam gists
- Search query and response models
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """Isometric Town building node or graph entity."""

    id: str
    name: str
    type: str = "CONCEPT"
    description: str = ""
    is_seed: bool = False
    community_id: int | None = None
    level: int = 1
    path_order: int | None = None


class GraphEdge(BaseModel):
    """Isometric Town road or directed semantic relationship."""

    source: str
    target: str
    relation: str = "CONNECTED_TO"
    description: str = ""
    weight: float = 1.0


class TownGraphResponse(BaseModel):
    """Complete graph payload for the isometric Town Map visualization."""

    document_id: str
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class StudySubtopicRead(BaseModel):
    id: str
    name: str
    summary: str = ""
    needs_context: bool = False


class StudyTopicRead(BaseModel):
    id: str
    name: str
    summary: str = ""
    subtopics: list[StudySubtopicRead] = Field(default_factory=list)
    conceptually_links_to: list[str] = Field(default_factory=list)


class StudySectionRead(BaseModel):
    id: str
    title: str
    summary: str = ""
    topics: list[StudyTopicRead] = Field(default_factory=list)


class StudyChapterRead(BaseModel):
    id: str
    title: str
    chapter_number: int | None = None
    sections: list[StudySectionRead] = Field(default_factory=list)


class StudyMapResponse(BaseModel):
    """Hierarchical textbook curriculum and flat graph representations."""

    document_id: str
    chapters: list[StudyChapterRead] = Field(default_factory=list)
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class CommunityRead(BaseModel):
    """Leiden community cluster report."""

    id: str | int
    title: str
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    rating: float = 8.0
    member_ids: list[str] = Field(default_factory=list)
    member_count: int = 0


class NodeDossierResponse(BaseModel):
    """Deep-dive dossier aggregating raw chunks, formula citations, and 1-hop links."""

    node_id: str
    name: str
    type: str = "CONCEPT"
    description: str = ""
    incoming_relations: list[GraphEdge] = Field(default_factory=list)
    outgoing_relations: list[GraphEdge] = Field(default_factory=list)
    text_chunks: list[dict[str, Any]] = Field(default_factory=list)


class LearningPathStep(BaseModel):
    """Curriculum step in pedagogical sequence."""

    step_index: int
    id: str
    name: str
    type: str = "TOPIC"
    summary: str = ""
    needs_context: bool = False
    prerequisites: list[str] = Field(default_factory=list)


class LearningPathResponse(BaseModel):
    """Topologically sorted curriculum steps with prerequisite gates."""

    document_id: str
    steps: list[LearningPathStep] = Field(default_factory=list)


class ExamGistResponse(BaseModel):
    """Rapid revision 2-minute exam summary."""

    document_id: str
    top_concepts: list[str] = Field(default_factory=list)
    key_formulas: list[str] = Field(default_factory=list)
    common_pitfalls: list[str] = Field(default_factory=list)
    likely_questions: list[str] = Field(default_factory=list)


class LocalSearchRequest(BaseModel):
    query: str
    top_k_seeds: int = 5
    top_k_chunks: int = 4


class GlobalSearchRequest(BaseModel):
    query: str

