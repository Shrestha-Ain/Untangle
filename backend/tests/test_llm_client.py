"""
Unit tests for LangChain model-agnostic LLM client, fallbacks, and prompt schemas.
"""

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from app.llm.client import (
    get_chat_model,
    get_extraction_model,
    get_synthesis_model,
    infer_provider,
)
from app.llm.prompts import (
    COMMUNITY_SUMMARY_PROMPT,
    EXAM_GIST_PROMPT,
    EXTRACTION_PROMPT,
    REGULUS_CHAT_PROMPT,
    STUDY_HIERARCHY_PROMPT,
    CommunitySummaryResult,
    ExamGistResult,
    ExtractedEntity,
    ExtractedRelationship,
    ExtractionResult,
    StudyHierarchyResult,
)


def test_infer_provider():
    """Verify model naming correctly infers provider."""
    assert infer_provider("gemini-3.5-flash-lite") == "google"
    assert infer_provider("gemini-2.5-flash") == "google"
    assert infer_provider("llama-3.3-70b-versatile") == "groq"
    assert infer_provider("mixtral-8x7b-32768") == "groq"
    assert infer_provider("claude-haiku-4-5") == "anthropic"
    assert infer_provider("gpt-4o-mini") == "openai"


def test_model_initialization_runnables():
    """Verify factory methods return configured LangChain ChatModels or Runnables with fallbacks."""
    extraction_runnable = get_extraction_model()
    assert extraction_runnable is not None

    synthesis_runnable = get_synthesis_model()
    assert synthesis_runnable is not None

    chat_runnable = get_chat_model()
    assert chat_runnable is not None


def test_automatic_fallback_execution():
    """Verify that when a primary model encounters an error, the fallback runnable seamlessly recovers."""
    call_counts = {"primary": 0, "fallback": 0}

    def failing_primary(messages):
        call_counts["primary"] += 1
        raise ConnectionError("429 Too Many Requests: Rate limit exceeded")

    def successful_fallback(messages):
        call_counts["fallback"] += 1
        return AIMessage(content="Fallback response generated successfully")

    primary = RunnableLambda(failing_primary)
    fallback = RunnableLambda(successful_fallback)

    resilient_chain = primary.with_fallbacks([fallback])
    result = resilient_chain.invoke("Explain attention")

    assert call_counts["primary"] == 1
    assert call_counts["fallback"] == 1
    assert result.content == "Fallback response generated successfully"


def test_prompt_formatting():
    """Verify all prompt templates format cleanly into messages."""
    # 1. Extraction prompt
    messages = EXTRACTION_PROMPT.format_messages(text="Test chunk text")
    assert len(messages) == 2
    assert "expert academic knowledge graph engineer" in messages[0].content
    assert "Test chunk text" in messages[1].content

    # 2. Study hierarchy prompt
    messages = STUDY_HIERARCHY_PROMPT.format_messages(text="Chapter 1 overview")
    assert len(messages) == 2

    # 3. Community summary prompt
    messages = COMMUNITY_SUMMARY_PROMPT.format_messages(entities_and_relationships="Node A -> Node B")
    assert len(messages) == 2

    # 4. Exam gist prompt
    messages = EXAM_GIST_PROMPT.format_messages(text="Key formulas: A = B + C")
    assert len(messages) == 2

    # 5. Regulus chat prompt
    messages = REGULUS_CHAT_PROMPT.format_messages(
        subgraph_context="Node1 connected to Node2",
        chunks_context="[Chunk 1] Attention paper snippet",
        question="What is attention?",
    )
    assert len(messages) == 2
    assert "You are Regulus" in messages[0].content
    assert "What is attention?" in messages[1].content


def test_pydantic_schema_validation():
    """Verify structured output Pydantic schemas."""
    # 1. ExtractionResult schema
    data = {
        "entities": [
            {
                "name": "Transformer",
                "type": "METHOD",
                "description": "Novel neural network architecture based solely on attention mechanisms.",
            }
        ],
        "relationships": [
            {
                "source": "Transformer",
                "target": "Multi-Head Attention",
                "relation": "INCORPORATES",
                "description": "Transformers rely on multi-head attention to model dependencies.",
                "weight": 0.95,
            }
        ],
    }
    result = ExtractionResult.model_validate(data)
    assert len(result.entities) == 1
    assert isinstance(result.entities[0], ExtractedEntity)
    assert isinstance(result.relationships[0], ExtractedRelationship)

    # 2. StudyHierarchyResult schema
    study_data = {
        "chapters": [
            {
                "title": "Introduction to Neural Networks",
                "chapter_number": 1,
                "sections": [
                    {
                        "title": "Perceptrons",
                        "summary": "Basic linear classifiers.",
                        "topics": [
                            {
                                "name": "Activation Functions",
                                "summary": "Adds non-linearity.",
                                "subtopics": [
                                    {
                                        "name": "ReLU",
                                        "summary": "Rectified Linear Unit.",
                                        "needs_context": False,
                                    }
                                ],
                                "conceptually_links_to": ["Perceptron"],
                            }
                        ],
                    }
                ],
            }
        ]
    }
    hierarchy = StudyHierarchyResult.model_validate(study_data)
    assert len(hierarchy.chapters) == 1
    assert hierarchy.chapters[0].sections[0].topics[0].name == "Activation Functions"

    # 3. CommunitySummaryResult schema
    comm_data = {
        "title": "Attention & Feed-Forward Sublayers",
        "summary": "This community encompasses the core computational blocks of transformer decoders.",
        "key_findings": ["Self-attention connects all positions", "Residual connections prevent vanishing gradients"],
        "rating": 9.5,
    }
    comm_summary = CommunitySummaryResult.model_validate(comm_data)
    assert comm_summary.rating == 9.5

    # 4. ExamGistResult schema
    gist_data = {
        "top_concepts": ["Scaled Dot-Product", "Positional Encoding"],
        "key_formulas": ["Softmax(QK^T / sqrt(d_k))V"],
        "common_pitfalls": ["Confusing multi-head attention with self-attention"],
        "likely_questions": ["Derive the scaling factor sqrt(d_k)"],
    }
    gist = ExamGistResult.model_validate(gist_data)
    assert len(gist.top_concepts) == 2

