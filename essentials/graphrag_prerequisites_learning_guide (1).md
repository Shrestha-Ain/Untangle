# GraphRAG Explorer — Prerequisites & Theory Guide

This is a standalone learning roadmap. Every topic includes: **what it is**, **why this project needs it**, and **where to learn it**. Organized in tiers — work through Tier 1 before you write any code; Tiers 2-4 can be learned alongside the corresponding week of the build order.

---

## TIER 1 — Core NLP & AI Concepts (must-understand before starting)

### 1.1 What an embedding actually is
An embedding is a vector of numbers (e.g., 384 or 1536 dimensions) that represents the *meaning* of a piece of text, such that texts with similar meaning end up geometrically close together in that vector space. "King" and "Queen" are close; "King" and "Banana" are far apart. This isn't magic — it comes from a model trained so that words/sentences appearing in similar contexts get pushed toward similar vectors.

**Why this project needs it:** every vector search in the app (finding seed entities, finding relevant chunks, finding relevant community summaries) works because you've converted text into these vectors and compare them by distance.

**Learn it via:** the "word2vec" intuition first (much simpler, same core idea) — 3Blue1Brown's neural network / word embedding videos are the best visual intuition. Then read about *contextual* embeddings (BERT-style) to understand why modern embeddings are better than word2vec: the same word gets a different vector depending on its sentence.

### 1.2 Cosine similarity
The standard way to measure "closeness" between two embedding vectors — it measures the angle between them, not raw distance, so it's insensitive to vector magnitude. Formula: `cos(θ) = (A · B) / (|A| |B|)`, ranges from -1 to 1, and in practice for text embeddings you'll see mostly 0 to 1, where closer to 1 means more similar.

**Why this project needs it:** it's the metric behind every vector search call (Qdrant), and it's also the metric used in entity deduplication (§6.5 of the system design) to decide if two entity descriptions are "the same thing."

### 1.3 Approximate Nearest Neighbor (ANN) search & HNSW
Finding the single closest vector to a query vector among millions is trivial in theory (just compute distance to everything) but too slow in practice at scale. ANN algorithms trade a small amount of accuracy for massive speed gains. **HNSW** (Hierarchical Navigable Small World graphs) is the dominant algorithm — it builds a multi-layer graph structure over your vectors so search can "jump" toward the right neighborhood instead of scanning everything.

**Why this project needs it:** Qdrant uses HNSW internally — you don't implement it yourself, but understanding *why* it exists (and that it's an approximation, not exact search) matters when you're explaining your system's retrieval latency/accuracy tradeoffs.

**Learn it via:** Qdrant's own documentation has a clear conceptual explanation; Pinecone's blog also has a well-regarded visual explainer of HNSW.

### 1.4 How LLMs actually generate text (practical level, not full transformer math)
At minimum, understand: an LLM predicts the next token given all previous tokens, one at a time, using a mechanism called **self-attention** that lets each token "look at" every other token in the context and decide which ones are relevant to predicting what comes next. This is why LLMs are good at using long context — attention lets a fact from 2000 tokens ago directly influence the next word.

**Why this project needs it:** explains why your prompt structure and context assembly (what you put *before* the question) directly determines answer quality — the model isn't "remembering" your document, it's attending over whatever text you put in its context window at that moment.

**Learn it via:** the original "Attention Is All You Need" paper (Vaswani et al., 2017) is genuinely readable at the conceptual level even if you skip the math; 3Blue1Brown's "Attention in transformers" video is an excellent visual companion. Stanford's CS224N lecture notes/videos on attention are the standard deeper reference if you want more rigor.

### 1.5 In-context learning & few-shot prompting
LLMs can perform a task better if you show them a few examples of input→output pairs directly in the prompt, without any additional training — this is called in-context learning, and it's *why* the extraction prompt in the implementation guide includes a worked example.

**Why this project needs it:** your entire extraction pipeline's quality depends on prompt engineering, and few-shot examples are the single highest-leverage lever you have.

### 1.6 Structured output / function calling / JSON mode
Modern LLM APIs support constraining the model's output to match a JSON schema exactly (rather than free text you hope is valid JSON). Anthropic calls this "tool use," OpenAI calls it "function calling" / `response_format`.

**Why this project needs it:** your extraction step needs machine-parseable output every single time — this is not optional at scale.

### 1.7 Named Entity Recognition (NER) and Relation Extraction as NLP tasks
NER is the classic NLP task of identifying spans of text that refer to entities (people, orgs, places) and classifying their type. Relation Extraction identifies the semantic relationship between two entities mentioned in text. Historically these were solved with dedicated trained models (spaCy, BERT-based taggers); this project solves them via LLM prompting instead, which trades some precision for zero-shot flexibility across any domain.

**Why this project needs it:** this *is* the extraction step — worth knowing this is a decades-old, well-studied NLP problem so you can speak to why LLM-based extraction is a reasonable modern approach versus training a dedicated model, and what you're trading off (interpretability and speed for flexibility).

### 1.8 Coreference resolution
The task of figuring out which words/phrases refer to the same real-world entity — "Marie Curie... she... the physicist... her research" all refer to one person. Unresolved coreference is the single biggest quality killer in naive entity extraction pipelines.

**Why this project needs it:** it's why your extraction prompt explicitly handles pronoun resolution within a chunk, and why you pass in a bit of previous-chunk context.

---

## TIER 2 — Graphs, Retrieval & Information Theory

### 2.1 Graph theory basics
A graph is a set of **nodes** (entities) connected by **edges** (relationships). Edges can be **directed** (A→B means something different from B→A) or **undirected**, and can carry **weights** (e.g., how many times a relationship was observed). Two core traversal algorithms: **BFS** (breadth-first search — explore all neighbors before going deeper, good for "shortest path" / N-hop expansion) and **DFS** (depth-first search — go as deep as possible before backtracking).

**Why this project needs it:** your "local search" retrieval mode is literally BFS-style N-hop graph expansion from seed entities — understanding why BFS (not DFS) is the right traversal for "find everything within 2 hops" is directly relevant to a system design conversation.

**Learn it via:** any standard algorithms course/textbook section on graphs (CLRS is the classic reference, but any intro course covers this adequately) — you need the intuition, not competitive-programming-level implementation speed.

### 2.2 Graph databases vs. relational databases
Relational databases (Postgres) are optimized for structured records with a fixed schema, joined via foreign keys. Graph databases (Neo4j) are optimized for traversing relationships — a "find everyone connected to X within 3 hops" query is a single fast graph traversal in Neo4j, but in Postgres it would require multiple expensive self-joins that get slower with every additional hop.

**Why this project needs it:** this is the core architectural justification for why the knowledge graph lives in Neo4j and not just another Postgres table — you should be able to explain this tradeoff clearly, since it's the most obvious "why did you choose this stack" question you'll get.

### 2.3 The Cypher query language
Neo4j's query language, structurally similar to SQL but pattern-based: `MATCH (a)-[:KNOWS]->(b) RETURN a, b` reads almost like ASCII art of the graph pattern you're looking for. Key clauses: `MATCH` (find a pattern), `MERGE` (find-or-create, used constantly in this project to avoid duplicate nodes), `CREATE`, `WHERE`, `RETURN`.

**Learn it via:** Neo4j's own GraphAcademy (free, official, interactive) is the most efficient path — a few hours gets you fully functional.

### 2.4 Modularity and community detection
**Modularity** is a mathematical measure of how well a graph is divided into clusters — high modularity means nodes within a cluster are densely connected to each other and sparsely connected to nodes outside it. **Louvain** algorithm greedily optimizes modularity by repeatedly merging nodes into communities that most improve the score, and does this hierarchically (communities of communities). **Leiden** algorithm (a refinement of Louvain) fixes a known flaw where Louvain can produce internally disconnected communities, guaranteeing well-connected communities instead.

**Why this project needs it:** this is precisely how your "global search" retrieval mode groups entities into meaningful clusters, which then get LLM-summarized — it's the mechanism that lets the system answer broad thematic questions instead of only specific fact lookups.

**Learn it via:** "From Louvain to Leiden: guaranteeing well-connected communities" (Traag, Waltman, van Eck, 2019) is the canonical paper and is readable at the conceptual level even without deep graph theory background — read the intro and motivation sections closely even if you skim the proofs.

### 2.5 Retrieval-Augmented Generation (RAG) — the general pattern
Instead of relying purely on an LLM's training-time knowledge, RAG retrieves relevant external information at query time and inserts it into the prompt, so the model generates an answer grounded in that retrieved content. Basic RAG = embed query → vector search → stuff top-k results into prompt → generate.

**Why this project needs it:** GraphRAG is a variant/extension of this basic pattern — you need to deeply understand plain RAG first to appreciate exactly what the graph structure is adding on top of it (multi-hop reasoning and thematic summarization that pure chunk retrieval can't do).

### 2.6 Sparse vs. dense retrieval, and why hybrid retrieval exists
**Sparse retrieval** (like BM25/TF-IDF) matches based on exact keyword overlap, weighted by term rarity — great for exact terms, names, and jargon, bad at synonyms/paraphrasing. **Dense retrieval** (embeddings) matches based on semantic similarity — great at paraphrasing, weaker on exact rare terms or numbers. **Hybrid retrieval** combines both, since they fail in different, complementary ways.

**Why this project needs it:** your query pipeline uses vector (dense) search for entities/chunks, and you could extend it with BM25 as a stretch goal — worth understanding why production RAG systems almost never rely on dense retrieval alone.

### 2.7 The actual GraphRAG paper
"From Local to Global: A Graph RAG Approach to Query-Focused Summarization" (Edge et al., Microsoft Research, 2024) is the paper this entire project reimplements the ideas of. Read it once lightly before starting (for the big picture: why community summaries solve the "summarize the whole corpus" problem that chunk-retrieval RAG handles poorly), and once carefully after you've built local search (to understand the map-reduce global search mechanism in enough detail to implement it correctly).

### 2.8 Precision, recall, and why they trade off
**Precision** = of the things you retrieved/predicted, what fraction were actually correct/relevant. **Recall** = of all the things that were actually correct/relevant, what fraction did you find. Improving one often costs the other (retrieve more aggressively → recall up, precision down).

**Why this project needs it:** it's the vocabulary you need for your evaluation section — when you report "GraphRAG improved multi-hop accuracy," you should also be able to speak to whether that came with a precision/recall tradeoff in what got retrieved.

### 2.9 Faithfulness / groundedness and hallucination
**Faithfulness** (or groundedness) measures whether a generated answer's claims are actually supported by the retrieved context, as opposed to being invented (hallucinated) by the model from its training data. This is typically measured by having a second LLM call act as a judge, checking each claim in the answer against the provided context.

**Why this project needs it:** it's your core evaluation metric (system design §11) and one of the main things RAG architectures exist to reduce, so you should be able to define it precisely, not just say "we check if the answer is good."

**Learn it via:** the RAGAS project's documentation is a practical, well-explained reference for this and several related metrics (context precision, context recall, faithfulness, answer relevance) — you don't need to use their library, but their metric definitions are the field-standard vocabulary.

---

## TIER 3 — Systems & Backend Engineering

### 3.1 Blocking vs. non-blocking I/O, and async/await
A **blocking** call (like a normal synchronous database query) makes your program sit idle waiting for a response, unable to do anything else. **Non-blocking/async** code lets the program work on other tasks while waiting — Python's `async`/`await` syntax, running inside an **event loop**, is how this is expressed. This matters enormously for I/O-bound workloads (waiting on network calls to databases and LLM APIs), much less for CPU-bound work.

**Why this project needs it:** this backend spends almost all its time waiting on Postgres, Neo4j, Qdrant, and LLM API calls — none of which are CPU-heavy — so async I/O lets one process handle many concurrent requests without needing a thread per request. This is the concrete reason FastAPI (async-native) fits this project better than a purely synchronous framework.

### 3.2 Producer-consumer pattern & message queues
A **producer** creates units of work and puts them on a queue; one or more **consumers** (workers) pull work off the queue and process it independently, at their own pace. This decouples "accepting a request" from "doing the (possibly slow) work," so your web server stays responsive.

**Why this project needs it:** this is exactly the relationship between your FastAPI upload endpoint (producer — enqueues an ingestion job and returns immediately) and your Celery workers (consumers — actually do the parsing/extraction/clustering, which can take minutes).

### 3.3 Celery's architecture (broker, worker, backend)
Celery needs a **broker** (Redis or RabbitMQ) to hold the queue of pending tasks, one or more **worker** processes that pull tasks and execute them, and optionally a **result backend** to store task outcomes. Celery primitives worth understanding precisely: a **chain** (run tasks in sequence, each fed the previous one's output), a **group** (run tasks in parallel, fan-out), and a **chord** (a group followed by a callback that only runs once every parallel task finishes) — the ingestion pipeline in this project uses all three.

### 3.4 Redis's three separate jobs in this stack
It's worth being explicit that Redis is doing three conceptually distinct things here, which is a good thing to be able to articulate: (1) **Celery's message broker** (queue of pending tasks), (2) **pub/sub channel** for relaying live ingestion progress to WebSocket clients, and (3) a plain **cache** for repeated query results. These could technically be three separate systems — using one Redis instance for all three is a deliberate simplicity tradeoff worth naming.

### 3.5 WebSockets vs. Server-Sent Events vs. polling
**Polling** — the client repeatedly asks "anything new?" on an interval; simple but wasteful and adds latency up to the poll interval. **Server-Sent Events (SSE)** — a one-way persistent connection from server to client, good for streaming (like LLM token output) where the client never needs to send more than the initial request. **WebSockets** — a full bidirectional persistent connection, needed when the client also needs to send messages back over the same connection (like a chat interface where the user keeps typing new questions).

**Why this project needs it:** you should be able to justify why chat uses WebSockets (bidirectional — user sends questions, server streams tokens back, repeatedly, on one connection) while a simpler broadcast-only progress bar could have used SSE instead — this project uses WebSockets for both mainly for implementation simplicity, and that's a fine tradeoff to name explicitly rather than pretend was a deep architectural decision.

### 3.6 JWT authentication & password hashing
A **JWT** (JSON Web Token) is a self-contained, digitally signed token (`header.payload.signature`) that encodes claims like user ID and expiry — the server can verify it's untampered-with using its secret key without needing to look up a session in a database, which is why it's called "stateless" auth. Passwords must never be stored in plaintext — they're run through a slow, salted **hashing** function (bcrypt or argon2) so that even if your database leaks, the original passwords aren't recoverable.

### 3.7 OAuth2 password flow
The specific auth pattern FastAPI's security utilities are built around: client sends username/password to a token endpoint, receives back an access token, then includes that token in an `Authorization: Bearer <token>` header on every subsequent request.

**Learn it via (3.6/3.7):** jwt.io has a genuinely useful interactive debugger that shows you exactly what's inside a real JWT — decode a few tokens there and the concept clicks immediately. FastAPI's own official security tutorial walks through the whole OAuth2 password flow implementation directly.

---

## TIER 4 — Frontend Concepts

### 4.1 Vue's reactivity system
Vue tracks which parts of your UI depend on which pieces of data, so that when a `ref()` or `reactive()` value changes, only the DOM nodes that actually depend on it re-render — you never manually call something like `render()` yourself. The **Composition API** (`<script setup>`, `ref`, `computed`, `watch`) organizes this by *logical concern* rather than by *option type*, which scales much better than the older Options API once a component has real complexity (as `GraphCanvas.vue` does).

### 4.2 Component communication: props/emit and composables
Parent-to-child data flows via **props**; child-to-parent communication flows via **emit**ting custom events. When logic (not just state) needs to be reused across components — like the WebSocket connection logic in `useWebSocket.ts` — Vue's convention is a **composable**: a plain function starting with `use` that encapsulates reactive state and behavior, importable into any component that needs it.

### 4.3 Centralized state management (Pinia)
When multiple components need to read/react to the same piece of state (in this app: the graph data, which components), passing props down through many layers gets unwieldy. Pinia provides a single centralized **store** that any component can read from or dispatch actions to directly, without prop-drilling.

**Why this project needs it:** `GraphCanvas.vue` and `ChatPanel.vue` are siblings that both need to react to the same subgraph-highlight state — Pinia is what lets the chat panel "tell" the graph canvas what to highlight without them being directly wired together.

### 4.4 Force-directed graph layout (conceptually)
Force-directed layout algorithms (like `fcose`, which this project uses) simulate a physical system: every node repels every other node (like same-charge particles), while edges act like springs pulling connected nodes together. Running this simulation until it settles produces a layout where densely connected clusters naturally group together visually, with minimal edge crossings.

**Why this project needs it:** this is *why* your graph visually clusters into recognizable groups without you manually positioning a single node — and it's directly complementary to the Leiden community detection happening on the backend (one clusters visually via physics, the other clusters structurally via graph algorithms; in a good demo, they visually agree with each other).

---

## TIER 5 — DevOps (lighter, but worth knowing)

### 5.1 Containers vs. images, and why Docker
An **image** is a frozen snapshot of an application plus its entire environment (OS libraries, dependencies, code) — a **container** is a running instance of that image. The core value proposition: "works on my machine" stops being a real problem, because the environment ships with the code.

### 5.2 Docker Compose
A tool for defining and running multiple containers together as one system, described declaratively in one YAML file (which is exactly what's in the deployment section of the system design doc) — `docker-compose up` starts your backend, frontend, Postgres, Neo4j, Qdrant, and Redis together, correctly networked to talk to each other.

### 5.3 CI/CD, minimally
**Continuous Integration**: automatically running tests/lint on every code push so bugs are caught before merging. **Continuous Deployment**: automatically shipping merged code to production without a manual deploy step. You don't need a deep DevOps background for this project — GitHub Actions with a fairly short YAML file covers both adequately for a portfolio project.

---

## Suggested Order to Actually Learn This

You do not need to sit down and learn all 20+ topics before touching code — that would take too long and most of it clicks far faster once you see it in use. A more efficient path:

1. **Before Week 1 of the build:** Tier 1 (1.1-1.4, 1.6) and Tier 3 (3.1, 3.6/3.7) — you cannot meaningfully write the extraction pipeline or auth without these.
2. **Before Week 2-3:** the rest of Tier 1 (1.5, 1.7, 1.8) and Tier 2's graph basics (2.1-2.3) — needed right as you start writing Cypher and extraction prompts.
2. **Before Week 4:** Tier 2's community detection and RAG sections (2.4-2.7) — this is the conceptual core of the whole project, don't rush it.
3. **Before Week 5-6:** the rest of Tier 3 (message queues, WebSockets) and all of Tier 4 — needed as you build the async pipeline and frontend.
4. **Before Week 8 (evaluation):** Tier 2's IR metrics (2.8, 2.9) — needed to write your evaluation report meaningfully rather than just eyeballing "the answers look good."

One last piece of advice: for a project like this, being able to **explain why you made each architectural choice** (why Neo4j and not just Postgres, why Leiden and not just Louvain, why hybrid retrieval, why async) matters more in an interview than having memorized every algorithm's mathematical proof. Aim for solid conceptual fluency on all of the above, and genuine depth on whichever 2-3 topics you find most interesting — that unevenness is normal and expected, and interviewers can tell the difference between "read about it once" and "actually reasoned about a tradeoff while building."
