# GraphRAG Explorer — Implementation Deep Dive

Companion to `graphrag_explorer_system_design.md`. Covers: (A) FastAPI project structure, (B) Vue + Cytoscape.js integration, (C) LLM extraction/synthesis prompt design.

---

# A. FastAPI Project Structure

## A.1 Directory Layout

```
backend/
├── app/
│   ├── main.py                    # app factory, mounts routers, CORS, startup/shutdown
│   ├── core/
│   │   ├── config.py               # Settings via pydantic-settings, reads .env
│   │   ├── security.py             # JWT encode/decode, password hashing
│   │   └── celery_app.py           # Celery instance + config
│   ├── api/
│   │   ├── deps.py                 # shared dependencies: get_db, get_current_user, get_neo4j
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── documents.py
│   │       ├── graph.py
│   │       ├── chat.py
│   │       └── ws.py                # WebSocket routes (progress + chat streaming)
│   ├── models/                      # SQLAlchemy ORM models (Postgres)
│   │   ├── user.py
│   │   ├── document.py
│   │   └── chat.py
│   ├── schemas/                     # Pydantic request/response contracts
│   │   ├── document.py
│   │   └── chat.py
│   ├── services/                    # business logic — the important layer
│   │   ├── extraction_service.py
│   │   ├── graph_service.py          # all Neo4j Cypher lives here, nowhere else
│   │   ├── vector_service.py         # all Qdrant calls live here
│   │   └── retrieval_service.py      # orchestrates local/global search
│   ├── tasks/                        # Celery task definitions
│   │   ├── ingestion.py
│   │   └── clustering.py
│   ├── llm/
│   │   ├── client.py                 # thin wrapper so provider is swappable
│   │   └── prompts.py                # all prompt templates, centralized
│   └── db/
│       ├── postgres.py               # SQLAlchemy engine + session factory
│       └── neo4j.py                  # Neo4j driver singleton
├── tests/
│   ├── test_extraction.py
│   └── test_retrieval.py
├── alembic/                          # Postgres migrations
├── requirements.txt
└── Dockerfile
```

**Why this layering matters (and is worth explaining in an interview):** routers should be thin — they parse the request, call a service, return the response. All Neo4j-specific Cypher lives only in `graph_service.py`; all Qdrant calls live only in `vector_service.py`. This means if you ever swap Neo4j for another graph DB, you touch one file, not fifteen. This separation (routers → services → data layer) is the single most common thing interviewers probe for when they ask "walk me through your codebase."

## A.2 Config (`core/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_url: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    qdrant_url: str
    redis_url: str
    jwt_secret: str
    llm_provider: str = "anthropic"       # "anthropic" | "openai"
    extraction_model: str = "claude-haiku-4-5"
    synthesis_model: str = "claude-sonnet-4-6"
    embedding_model: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"

settings = Settings()
```

Loading all config through one typed object (rather than scattered `os.environ.get()` calls) means misconfiguration fails fast at startup instead of silently at 2am in production.

## A.3 Shared Dependencies (`api/deps.py`)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.db.postgres import SessionLocal
from app.db.neo4j import get_driver
from app.core.security import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_neo4j():
    driver = get_driver()
    try:
        yield driver
    finally:
        pass  # driver is a long-lived singleton, don't close per-request

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return user
```

`Depends()` is FastAPI's dependency-injection system — each request gets its own DB session, cleanly closed afterward, and `get_current_user` is composable into any route that needs auth just by adding it as a parameter.

## A.4 Example Router (`api/v1/documents.py`)

```python
from fastapi import APIRouter, Depends, UploadFile, File
from app.api.deps import get_db, get_current_user
from app.schemas.document import DocumentOut
from app.tasks.ingestion import run_ingestion_pipeline
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    document = document_service.create_document(db, user.id, file.filename)
    contents = await file.read()
    document_service.save_raw_file(document.id, contents)

    # enqueue the Celery chain, return immediately — don't block the request
    run_ingestion_pipeline.delay(str(document.id))

    return document

@router.get("", response_model=list[DocumentOut])
def list_documents(db=Depends(get_db), user=Depends(get_current_user)):
    return document_service.list_for_user(db, user.id)
```

Note the router does almost nothing itself — it validates the upload, delegates persistence to `document_service`, and fires off the async job. This is the "thin router, fat service" pattern.

## A.5 Graph Service Example (`services/graph_service.py`)

```python
from app.db.neo4j import get_driver

def write_triple(source: dict, target: dict, relation: str, description: str, chunk_id: str):
    query = """
    MERGE (e1:Entity {name: $source_name})
      ON CREATE SET e1.id = randomUUID(), e1.type = $source_type, e1.description = $source_desc
    MERGE (e2:Entity {name: $target_name})
      ON CREATE SET e2.id = randomUUID(), e2.type = $target_type, e2.description = $target_desc
    MERGE (e1)-[r:RELATES_TO {relation_type: $relation}]->(e2)
      ON CREATE SET r.description = $desc, r.source_chunk_id = $chunk_id, r.weight = 1
      ON MATCH SET r.weight = r.weight + 1
    """
    with get_driver().session() as session:
        session.run(query,
            source_name=source["name"], source_type=source["type"], source_desc=source["description"],
            target_name=target["name"], target_type=target["type"], target_desc=target["description"],
            relation=relation, desc=description, chunk_id=chunk_id)

def expand_subgraph(seed_entity_ids: list[str], max_hops: int = 2):
    query = """
    MATCH (seed:Entity) WHERE seed.id IN $ids
    CALL apoc.path.subgraphAll(seed, {maxLevel: $hops, relationshipFilter: "RELATES_TO"})
    YIELD nodes, relationships
    RETURN nodes, relationships
    """
    with get_driver().session() as session:
        result = session.run(query, ids=seed_entity_ids, hops=max_hops)
        return result.single()
```

## A.6 Retrieval Orchestration (`services/retrieval_service.py`)

```python
from app.services import vector_service, graph_service
from app.llm.client import llm_complete
from app.llm.prompts import CLASSIFY_QUERY_PROMPT, SYNTHESIS_PROMPT

async def answer_question(question: str, document_id: str) -> dict:
    mode = await classify_query(question)   # "local" or "global"

    if mode == "local":
        seed_ids = vector_service.search_entities(question, document_id, top_k=5)
        subgraph = graph_service.expand_subgraph(seed_ids, max_hops=2)
        chunk_hits = vector_service.search_chunks(question, document_id, top_k=5)
        context = build_local_context(subgraph, chunk_hits)
    else:
        communities = graph_service.get_top_communities(document_id, question, top_k=8)
        context = build_global_context(communities)  # map-reduce happens inside here

    answer = await llm_complete(SYNTHESIS_PROMPT.format(question=question, context=context))
    return {"answer": answer, "mode": mode, "subgraph": subgraph}

async def classify_query(question: str) -> str:
    result = await llm_complete(CLASSIFY_QUERY_PROMPT.format(question=question))
    return "global" if "global" in result.lower() else "local"
```

This function is the single most important piece of business logic in the whole backend — it's the literal implementation of "GraphRAG" as opposed to plain RAG, and it's exactly what you'd walk an interviewer through on a whiteboard.

## A.7 Celery Task Chain (`tasks/ingestion.py`)

```python
from celery import chain, group, chord
from app.core.celery_app import celery_app
from app.services import extraction_service, graph_service, vector_service

@celery_app.task
def parse_document(document_id: str): ...

@celery_app.task
def chunk_document(document_id: str) -> list[str]: ...  # returns chunk_ids

@celery_app.task
def extract_from_chunk(chunk_id: str): ...  # one chunk, one LLM call

@celery_app.task
def deduplicate_entities(document_id: str, _extraction_results): ...

@celery_app.task
def embed_and_cluster(document_id: str): ...

@celery_app.task
def summarize_communities(document_id: str): ...

def run_ingestion_pipeline(document_id: str):
    chunk_ids = chunk_document(document_id)
    workflow = chain(
        parse_document.s(document_id),
        chord(
            group(extract_from_chunk.s(cid) for cid in chunk_ids),
            deduplicate_entities.s(document_id)
        ),
        embed_and_cluster.s(document_id),
        summarize_communities.s(document_id),
    )
    workflow.apply_async()
```

The `chord` is the key Celery primitive here: it fans out extraction across all chunks **in parallel**, then waits for every single one to finish before running deduplication — because dedup needs the full picture of every entity mentioned in the document, not just one chunk's worth.

---

# B. Vue 3 + Cytoscape.js Integration

## B.1 GraphCanvas.vue

```vue
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import cytoscape, { Core } from 'cytoscape'
import fcose from 'cytoscape-fcose'
import { useGraphStore } from '@/stores/graph'

cytoscape.use(fcose)

const containerRef = ref<HTMLElement | null>(null)
let cy: Core | null = null
const graphStore = useGraphStore()

const nodeColors: Record<string, string> = {
  PERSON: '#6366f1', ORG: '#f59e0b', CONCEPT: '#10b981',
  LOCATION: '#ef4444', DEFAULT: '#9ca3af',
}

onMounted(() => {
  cy = cytoscape({
    container: containerRef.value,
    elements: [],
    style: [
      {
        selector: 'node',
        style: {
          'background-color': (ele: any) => nodeColors[ele.data('type')] ?? nodeColors.DEFAULT,
          label: 'data(label)',
          'font-size': 10,
          color: '#1f2937',
          width: (ele: any) => 20 + Math.min(ele.data('mentionCount') ?? 1, 10) * 3,
          height: (ele: any) => 20 + Math.min(ele.data('mentionCount') ?? 1, 10) * 3,
        },
      },
      { selector: 'edge', style: { width: 1.5, 'line-color': '#d1d5db', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle' } },
      { selector: '.dimmed', style: { opacity: 0.15 } },
      { selector: '.highlighted', style: { opacity: 1, 'border-width': 3, 'border-color': '#facc15' } },
    ],
    layout: { name: 'fcose', animate: true, randomize: false },
  })

  cy.on('tap', 'node', (evt) => {
    graphStore.selectEntity(evt.target.data('id'))
  })

  graphStore.fetchGraph().then(() => renderGraph())
})

function renderGraph() {
  if (!cy) return
  cy.elements().remove()
  cy.add(graphStore.cytoscapeElements)   // [{data: {id, label, type, mentionCount}}, {data: {source, target}}]
  cy.layout({ name: 'fcose', animate: true }).run()
}

// Watch for a new chat answer's subgraph and highlight it
watch(() => graphStore.highlightedSubgraph, (subgraph) => {
  if (!cy || !subgraph) return
  cy.elements().addClass('dimmed').removeClass('highlighted')
  subgraph.nodeIds.forEach((id: string) => cy!.getElementById(id).removeClass('dimmed').addClass('highlighted'))
  subgraph.edgeIds.forEach((id: string) => cy!.getElementById(id).removeClass('dimmed').addClass('highlighted'))
})
</script>

<template>
  <div ref="containerRef" class="w-full h-full bg-gray-50 rounded-lg" />
</template>
```

**Design notes worth understanding, not just copying:**
- Node size scales with `mentionCount` — visually, entities that come up often in the source document look "heavier." This is a small touch that reads as polish in a demo.
- `fcose` (fast Compound Spring Embedder) is chosen over Cytoscape's default `cose` layout because it converges faster and handles a few thousand nodes better — worth naming this choice explicitly if asked "why this layout algorithm."
- The dim/highlight mechanic (`.dimmed` / `.highlighted` CSS classes) is what makes the chat-to-graph connection visually obvious — this is the single highest-impact UI detail in the whole app.

## B.2 `stores/graph.ts` (Pinia)

```typescript
import { defineStore } from 'pinia'
import { api } from '@/api/client'

export const useGraphStore = defineStore('graph', {
  state: () => ({
    nodes: [] as any[],
    edges: [] as any[],
    highlightedSubgraph: null as { nodeIds: string[]; edgeIds: string[] } | null,
    selectedEntityId: null as string | null,
  }),
  getters: {
    cytoscapeElements: (state) => [
      ...state.nodes.map(n => ({ data: { id: n.id, label: n.name, type: n.type, mentionCount: n.mention_count } })),
      ...state.edges.map(e => ({ data: { id: e.id, source: e.source_id, target: e.target_id } })),
    ],
  },
  actions: {
    async fetchGraph(documentId: string) {
      const { data } = await api.get(`/graph/${documentId}`)
      this.nodes = data.nodes
      this.edges = data.edges
    },
    applyHighlight(subgraph: { nodeIds: string[]; edgeIds: string[] }) {
      this.highlightedSubgraph = subgraph
    },
    selectEntity(id: string) {
      this.selectedEntityId = id
    },
  },
})
```

## B.3 `composables/useWebSocket.ts` (streaming chat)

```typescript
import { ref } from 'vue'

export function useChatSocket(sessionId: string, onSubgraph: (sg: any) => void) {
  const streamedText = ref('')
  const isStreaming = ref(false)
  let socket: WebSocket

  function connect() {
    socket = new WebSocket(`${import.meta.env.VITE_WS_URL}/ws/chat/${sessionId}`)
    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      if (msg.type === 'token') {
        streamedText.value += msg.content
      } else if (msg.type === 'done') {
        isStreaming.value = false
        onSubgraph(msg.subgraph)
      }
    }
  }

  function sendQuestion(question: string) {
    streamedText.value = ''
    isStreaming.value = true
    socket.send(JSON.stringify({ question }))
  }

  return { streamedText, isStreaming, connect, sendQuestion }
}
```

`ChatPanel.vue` then just calls `applyHighlight` (from the graph store) inside the `onSubgraph` callback — this is the wiring that connects "an answer arrived" to "the graph should react."

---

# C. LLM Extraction & Synthesis Prompt Design

Prompt design here is not "ask nicely" — it's schema-constrained structured generation, and the quality of your whole graph depends on getting this right. All prompts live in `llm/prompts.py`, and every extraction call uses **temperature 0** (deterministic) and **JSON-schema-constrained output** (via the provider's structured output / tool-use feature) rather than hoping the model returns valid JSON in free text.

## C.1 Entity & Relationship Extraction Prompt

```
SYSTEM:
You are an information extraction engine. Extract entities and relationships from the
given text chunk with high precision. Only extract what is explicitly stated or
directly implied — do not infer relationships that require outside knowledge.

Entity types allowed: PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, OTHER.

Return ONLY valid JSON matching this schema:
{
  "entities": [{"name": str, "type": str, "description": str}],
  "relationships": [{"source": str, "target": str, "relation": str, "description": str}]
}

Rules:
- "name" must be the canonical form used in the text (prefer full names over pronouns).
- "description" is a 1-sentence grounding of what this entity/relationship IS, based only
  on this chunk — this will later be used to deduplicate entities across chunks, so be specific.
- Do not invent relationships between entities that aren't connected in the text.
- If a pronoun clearly refers to an entity named earlier IN THIS CHUNK, resolve it to that
  entity's name rather than extracting the pronoun as a separate entity.

FEW-SHOT EXAMPLE:
Text: "Marie Curie, a physicist and chemist, conducted pioneering research on
radioactivity. She was the first woman to win a Nobel Prize."

Output:
{
  "entities": [
    {"name": "Marie Curie", "type": "PERSON", "description": "Physicist and chemist who conducted pioneering research on radioactivity"},
    {"name": "Nobel Prize", "type": "CONCEPT", "description": "Prestigious award; Marie Curie was the first woman to win one"}
  ],
  "relationships": [
    {"source": "Marie Curie", "target": "Nobel Prize", "relation": "WON", "description": "Marie Curie was the first woman to win a Nobel Prize"}
  ]
}

USER:
Text chunk (include ~1 sentence of context from the previous chunk for coreference):
{prev_context}
---
{chunk_text}
```

**Why the few-shot example matters more than the instructions:** LLMs follow demonstrated format far more reliably than described format. If your extraction quality is inconsistent, adding 2-3 few-shot examples (including one deliberately tricky case, like a chunk with an ambiguous pronoun) fixes it faster than rewriting the instructions.

**Why you include the previous chunk's last sentence:** without it, a chunk that opens with "He then moved to Paris" has no idea who "He" is — this is the single biggest cause of bad extractions in a naive chunk-by-chunk pipeline, and it's a detail worth explicitly mentioning as a design decision you made deliberately.

## C.2 Entity Disambiguation Prompt (dedup borderline cases)

```
SYSTEM:
You are resolving whether two entity mentions refer to the SAME real-world entity.
Answer with only "SAME" or "DIFFERENT", followed by a one-sentence reason.

USER:
Entity A: "{name_a}" — {description_a}
Entity B: "{name_b}" — {description_b}

Context: these appeared in the same document with a semantic similarity score of {score}.
```

This is only called for the "gray zone" (similarity 0.75-0.88 in the design doc) — most merges are handled automatically by exact match or high similarity, so this LLM call only fires for genuinely ambiguous cases, keeping cost down.

## C.3 Query Classification Prompt

```
SYSTEM:
Classify the user's question as either "local" or "global".
- "local": asks about a specific entity, fact, or relationship (who/what/when/where questions,
  or "how is X connected to Y").
- "global": asks about overall themes, summaries, or patterns across the whole document
  ("what are the main topics", "summarize the key arguments", "what patterns emerge").

Respond with only one word: local or global.

USER:
{question}
```

## C.4 Community Summarization Prompt

```
SYSTEM:
You will be given a cluster of related entities and the relationships between them,
extracted from a larger document. Write a concise 2-4 sentence summary describing what
this cluster is collectively "about" — the shared theme, event, or subject connecting
these entities. Write it as if summarizing a sub-topic of the source document for
someone who hasn't read it.

USER:
Entities in this cluster:
{entity_list_with_descriptions}

Relationships within this cluster:
{relationship_list_with_descriptions}
```

This runs once per community after Leiden clustering — the resulting summaries are what power "global search" (§7.3 of the system design doc), since a broad question gets answered by reading these summaries rather than the raw graph.

## C.5 Final Answer Synthesis Prompt

```
SYSTEM:
Answer the user's question using ONLY the provided context (entities, relationships, and
source text excerpts). If the context is insufficient to answer confidently, say so
explicitly rather than guessing.

For every claim in your answer, cite the source using [doc:chunk] notation matching the
IDs given in the context.

USER:
Question: {question}

Context:
{assembled_context}
```

The explicit "say so explicitly rather than guessing" instruction is a small but real lever on hallucination rate — it gives the model an easy, socially-acceptable path to admit insufficient context instead of confabulating an answer to seem helpful, and it's exactly the kind of instruction your faithfulness eval (system design §11) will let you measure the effect of.

## C.6 Implementation Tips

- **Validate every LLM JSON response with a Pydantic model** immediately after the call; on `ValidationError`, retry once with the error message appended to the prompt ("Your previous response failed validation with error: {error}. Return corrected JSON."). This single pattern eliminates most of the flakiness people associate with "LLMs don't reliably return JSON."
- **Use the provider's native structured output feature** (Anthropic tool-use / OpenAI `response_format={"type": "json_schema"}`) rather than just instructing "return JSON" in the prompt — this constrains the model's decoding directly and is far more reliable than prompt-only enforcement.
- **Keep extraction and synthesis prompts in version-controlled files, not inline strings scattered through the codebase** — when you're iterating on extraction quality, you want a clean diff history of exactly what prompt produced what eval score.
