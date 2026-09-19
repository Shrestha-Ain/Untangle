# Untangle — GraphRAG Backend Model Selection & Task Guide

This guide details all LLM and embedding tasks required by Untangle's GraphRAG backend, establishes task-to-model criteria, and provides curated **free-tier** and **budget-paid** model recommendations to maximize extraction quality, multi-hop reasoning, and exam preparation speed while minimizing or eliminating API spend.

---

## 1. Untangle GraphRAG Pipeline Tasks: What the Model Must Do

Unlike basic vector RAG (which only requires chunk embedding and single-turn query synthesis), Microsoft GraphRAG and Untangle's dual-mode system (Research Mode for papers and Study Mode for textbooks) involve **9 distinct LLM & embedding tasks** across the ingestion and retrieval lifecycle:

```
                          ┌────────────────────────┐
                          │   Document Ingestion   │
                          └───────────┬────────────┘
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
       [Research Mode: Papers]                       [Study Mode: Books]
  ┌───────────────────────────────┐             ┌───────────────────────────────┐
  │ Task 1: Entity/Relation Extr. │             │ Task 3: Structural Hierarchy  │
  │ Task 2: Entity Disambiguation │             │ Task 4: Concept Links & Scope │
  └──────────────┬────────────────┘             └───────────────┬───────────────┘
                 │                                              │
                 ├──────────────────────┬───────────────────────┤
                 ▼                      ▼                       ▼
          [Graph Clustering]    [Dense Vectors]        [Exam Prep Mode]
          Task 5: Community     Task 6: Dense Text     Task 8: High-Yield
            Summarization          Embeddings             Exam Gists
                 │                      │                       │
                 └──────────────────────┼───────────────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │  Online Retrieval & Chat  │
                          │  Task 7: Graph Traversal  │
                          │     & Regulus Synthesis   │
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │    Evaluation Harness     │
                          │  Task 9: Faithfulness     │
                          │     & LLM-as-a-Judge      │
                          └───────────────────────────┘
```

---

### Task Breakdown & Technical Specifications

| # | Task Name | Inputs & Context | Output Format | Volume / Frequency | Key Quality Metric |
|---|---|---|---|---|---|
| **1** | **Entity & Relation Extraction** *(Research Mode)* | ~500-token chunk + schema extraction prompt | Strict JSON array of nodes `(name, type, description)` & edges `(source, target, relation, description)` | **High** (30–120 calls per paper) | Zero schema breakage, high precision on entity types (`PERSON`, `ORG`, `CONCEPT`, `LOCATION`), verbatim grounding |
| **2** | **Entity Disambiguation & Merging** | Candidate pairs of similar entity names + text descriptions | JSON boolean `is_same_entity`, canonical merged name, merged description | **Medium** (15–50 pairs per document) | Deduplication recall, avoiding false collapses of distinct concepts |
| **3** | **Structural Hierarchy Extraction** *(Study Mode)* | 4,000–8,000 token book sections + TOC context | Hierarchical JSON tree: `Chapter → Section → Topic → Subtopic` with parent refs & summaries | **Low–Medium** (10–40 calls per textbook) | Parent-child link consistency, clean nesting, concise 2-sentence topic coverage |
| **4** | **Concept Linking & Outside Scope Flagging** *(Study Mode)* | Extracted topics from a chapter | JSON array of `CONCEPTUALLY_LINKS` edges + `needs_context=True` flags with explanation | **Low** (5–20 calls per textbook) | Accurate dependency detection, identifying prerequisites outside the book |
| **5** | **Hierarchical Community Summarization** *(GraphRAG Global Search)* | Cluster of entity nodes and relationship descriptions from Leiden algorithm | JSON object: `title`, `summary` (150–300 words), `findings` (3–5 bullet points), `weight_rating` | **Low** (5–25 communities per document) | Thematic synthesis, high-level abstraction without losing grounding |
| **6** | **Dense Text Embeddings** | Document chunks, entity descriptions, community summaries, and user queries | Dense float vector (e.g. 384, 768, or 1536 dims) | **High** (100–1,000+ vector calls per document) | MTEB retrieval benchmark score, semantic clustering quality in Qdrant |
| **7** | **Graph Traversal & Regulus Query Synthesis** | User query + retrieved subgraph triplets + chunk excerpts + conversation history | Real-time streaming markdown with citation bracket tokens `[Chunk X]` | **Real-Time** (1 call per user chat message) | High faithfulness, zero hallucination, multi-hop reasoning across interconnected nodes |
| **8** | **High-Yield Exam Gist Generation** | Chapter nodes, core topic descriptions, formulas/rules | Structured JSON: rank `#1..#N`, 2-sentence core summary, formula to memorize, likely exam question, common trap | **On-Demand / Batch** (1 pass per document) | Pedagogical sharpness, spotting common exam misconceptions, formula fidelity |
| **9** | **Faithfulness & Verification Scoring** *(Eval)* | Generated answer + retrieved ground truth context chunks | JSON: score `0.0–1.0`, binary citation accuracy, chain-of-thought rationale | **Offline / Eval** (Batch per evaluation run) | Calibration against human judgements, consistency across evaluation runs |

---

## 2. Model Tiering Strategy: Why One Model Shouldn't Do Everything

A common mistake in RAG systems is routing every task to a single expensive model (e.g., Claude 3.5 Sonnet or GPT-4o). In GraphRAG, this results in bloated bills because **Task 1 (chunk extraction) accounts for 75–85% of all LLM calls during ingestion**.

### The Optimal Two-Tier Architecture:
1. **Tier 1 — High-Throughput "Extractor Workhorse"**:
   - Handles **Tasks 1, 2, 3, 4, and 5**.
   - Priorities: Extremely low cost (or free), fast token generation, strict JSON output compliance, large context window (for long chapter windows in Study Mode).
2. **Tier 2 — High-Reasoning "Synthesizer & Guide (Regulus)"**:
   - Handles **Tasks 7, 8, and 9**.
   - Priorities: Complex multi-hop synthesis, adherence to grounding context, fast first-token latency for interactive streaming chat, pedagogical clarity.
3. **Embeddings Layer**:
   - Handles **Task 6**.
   - Dedicated small embedding model (either run locally on CPU for $0 or via an ultra-cheap embedding API).

---

## 3. Multiple Good FREE Options

For developing, testing, and portfolio demonstrations, you can run Untangle's entire GraphRAG pipeline for **$0.00** without spending anything on API credits.

### Free Option 1: Google Gemini 2.5 Flash & 2.5 Flash-Lite (via Google AI Studio)
*The highest daily throughput and largest context window available on any free tier.*

- **Provider**: Google AI Studio ([aistudio.google.com](https://aistudio.google.com))
- **Current Model Lineup**:
  - **`gemini-2.5-flash`**: Default multimodal workhorse with built-in thinking budget.
  - **`gemini-2.5-flash-lite`**: High-throughput, cost-efficient variant built for high-volume batch extraction.
  - **`gemini-2.0-flash`**: Predecessor high-speed flash model.
- **Free Tier Limits (Current Enforced Quotas)**:
  - **`gemini-2.5-flash`**:
    - **10 to 15 RPM** (Requests Per Minute)
    - **250,000 TPM** (Tokens Per Minute)
    - **250 to 1,500 RPD** (Requests Per Day, dynamic per project)
  - **`gemini-2.5-flash-lite`**:
    - **30 RPM**
    - **65,000 to 250,000 TPM**
    - **1,500 RPD**
  - **`gemini-2.5-pro`** *(Warning)*: Heavily throttled on free tier to **2–5 RPM**, **32,000 TPM**, **50 RPD**. Do not use for batch ingestion.
- **Important Quota Mechanics**:
  - **Project-Level Enforcement**: Quotas are pooled at the **Google Cloud Project** level, not per API key. Generating multiple keys within the same project shares the identical quota.
  - **Daily Reset**: RPD quotas reset at midnight Pacific Time (PT).
  - **Free Tier Data Logging**: On the free tier, Google may log and human-review prompts and completions to improve Google products. (Paid tier disables this).
- **Context Window**: 1,000,000 tokens (can process whole chapters or entire textbooks in a single prompt).
- **Why it fits Untangle**:
  - Native **Structured JSON schema output** (`response_mime_type="application/json"` with Pydantic validation).
  - 1,500 requests/day enables ingesting **30–50 research papers or multiple textbooks daily at zero cost**.
  - High generation speed (~150–200 tokens/sec).
- **Best Tasks**:
  - `gemini-2.5-flash-lite` $\rightarrow$ Task 1 (Entity/Relation extraction), Task 2 (Disambiguation), Task 3 (Structural hierarchy).
  - `gemini-2.5-flash` $\rightarrow$ Task 4 (Concept linking), Task 5 (Community summaries), Task 8 (Exam Gists).

### Free Option 2: Groq Cloud (Llama 3.3 70B & Llama 3.1 8B)
*The fastest streaming inference engine in the world, with critical daily token caps.*

- **Provider**: Groq Cloud ([console.groq.com](https://console.groq.com))
- **Current Free Tier Limits (Per Organization)**:
  - **`llama-3.3-70b-versatile`**:
    - **30 RPM**
    - **12,000 TPM** (Tokens Per Minute burst cap)
    - **1,000 RPD** (Requests Per Day)
    - **100,000 TPD (Tokens Per Day)** $\leftarrow$ **CRUCIAL BOTTLENECK**
  - **`llama-3.1-8b-instant`**:
    - **30 RPM**
    - **6,000 to 20,000 TPM**
    - **14,400 RPD**
    - **500,000 TPD (Tokens Per Day)**
- **Speed**: **300 to 750 tokens per second** on Groq's custom LPUs.
- **⚠️ The 100,000 TPD Architectural Bottleneck (Must Understand for GraphRAG)**:
  - In GraphRAG, extracting entities and relationships from a single 10–15 page paper requires ~25 chunks. With few-shot instructions, each chunk call consumes ~1,500 input tokens and generates ~400 output tokens $\approx$ **~45,000 tokens per paper**.
  - If you attempt to use `llama-3.3-70b-versatile` for Task 1 chunk extraction, **you will burn through the entire 100,000 TPD quota after just 2 papers**, triggering `429 Too Many Requests` that locks your Groq organization for 24 hours.
  - Furthermore, the **12,000 TPM** limit prevents concurrent chunk extraction (max ~6 chunks per minute).
- **The Correct Architectural Allocation**:
  - **DO NOT** use Groq 70B for Task 1 chunk extraction.
  - **USE Groq 70B strictly for Task 7 (Regulus Interactive Chat)**: A single chat question consumes ~800 tokens total. 100,000 TPD allows **120+ interactive chat queries per day** with mind-blowing `<150ms` streaming latency.
  - **USE Groq 8B** (500,000 TPD) if you want fast chunk extraction on Groq (~10–12 papers/day), or use Gemini 2.5 Flash / Flash-Lite where daily token caps do not bind.

### Free Option 3: Local / Open-Source via Ollama (100% Offline & Private)
*Zero API keys, zero rate limits, runs directly on your machine.*

- **Provider**: Ollama ([ollama.com](https://ollama.com)) running locally.
- **Recommended Models**:
  - **Qwen 2.5 7B / 14B Instruct**: Best-in-class open model for structured JSON extraction and technical reasoning. 7B fits easily in 8 GB VRAM (or system RAM via GGUF `q4_k_m`); 14B fits in 12–16 GB VRAM.
  - **Llama 3.2 3B Instruct**: Super-lightweight, runs at 60+ tokens/sec even on modest laptop CPUs.
  - **Mistral NeMo 12B Instruct**: 128k context window, excellent multilingual extraction.
- **Why it fits Untangle**:
  - Complete privacy: users can upload sensitive textbooks or proprietary papers without external cloud API calls.
  - No rate limits or network latency.
  - Compatible with FastAPI using standard `openai.OpenAI(base_url="http://localhost:11434/v1")`.
- **Best Tasks**: Tasks 1, 2, 3, 4, 7 (when offline).

### Free Option 4: Hugging Face Serverless Inference API (Qwen 2.5 72B & DeepSeek)
*Query 70B+ parameter flagship models without local GPU hardware.*

- **Provider**: Hugging Face Inference Providers / Router ([huggingface.co](https://huggingface.co))
- **Pricing**: **100% Free** with a free Hugging Face User Access Token (`hf_...`).
- **Endpoint**: Standard OpenAI-compatible API at `https://router.huggingface.co/hf-inference/v1`.
- **Supported Models**:
  - **`Qwen/Qwen2.5-72B-Instruct`**: Exceptional instruction following, world-class structured JSON handling, and deep mathematical reasoning.
  - **`Qwen/Qwen2.5-Coder-32B-Instruct`**: Highly tuned for code syntax, LaTeX formulas, and schema extraction.
  - **`deepseek-ai/DeepSeek-R1` / `DeepSeek-V3`**: Flagship reasoning architectures for multi-hop graph path validation.
- **Why it fits Untangle**:
  - Enables running massive 72B models without paying cloud hosting or needing an enterprise GPU cluster.
  - Ideal for **Task 7 (Regulus Synthesis)** and **Task 8 (Exam Gists)** where single-call depth and high reasoning matter most.
- **Caveats to Handle**:
  - **Cold starts (HTTP 503)**: If a model is idle, HF wakes it up on demand (~20–40s delay). Requires retry wrappers.
  - **Rate limits**: Best paired with Gemini Flash for high-volume Task 1 extraction (30–60 calls/paper) to avoid 429 concurrency throttles.

### Free Option 5: Free Dense Embeddings (Local & Serverless)
*Never pay for vector embeddings.*

- **Models**:
  - **`BAAI/bge-small-en-v1.5`** (384 dims, HuggingFace): Top performer on the MTEB leaderboard for its size class. Runs on CPU in 10ms via `fastembed` or `sentence-transformers`.
  - **`BAAI/bge-m3`** (1024 dims): Multi-lingual, dense + sparse hybrid search support, 8192 token chunk support.
  - **`sentence-transformers/all-MiniLM-L6-v2`** (384 dims): Ultra-compact (80MB), rock solid.
  - **`nomic-embed-text`** (via Ollama or Nomic free tier): 8192 context window.
  - **Google `text-embedding-004`** (via Gemini API): 768 dims, 1,500 free requests/day.
- **Best Tasks**: Task 6 (Dense Vector Embeddings for chunks, entities, and Qdrant).

---

## 4. Multiple PAID BUT CHEAP Options (Sub-$1 Scale)

When you want commercial-grade reliability without rate limit anxieties, these models offer top-tier performance for pennies:

### Paid Option 1: DeepSeek-V3 & DeepSeek-R1
*The industry standard for budget high-intelligence computing.*

- **Provider**: DeepSeek Official API ([deepseek.com](https://www.deepseek.com)) or OpenRouter.
- **Pricing**:
  - **DeepSeek-V3**: **$0.14 / 1M input tokens**, **$0.28 / 1M output tokens** (with prompt cache hits: **$0.014 / 1M input**).
  - **DeepSeek-R1** (Reasoning): **$0.55 / 1M input**, **$2.19 / 1M output**.
- **Why it fits Untangle**:
  - Over **90% cheaper than Claude 3.5 Haiku and GPT-4o-mini**.
  - DeepSeek-V3 matches Claude 3.5 Sonnet and GPT-4o on coding and technical extraction benchmarks.
  - DeepSeek-R1's chain-of-thought reasoning is ideal for multi-hop graph path validation and complex cross-paper linking.
- **Typical Document Cost**: Less than **$0.01 per 20-page paper**.

### Paid Option 2: Google Gemini 2.5 Flash & 2.5 Flash-Lite (Pay-As-You-Go Tier)
*Massive context window, commercial data privacy, and uncapped daily throughput.*

- **Provider**: Google AI Studio / Google Cloud Vertex AI
- **Pricing**:
  - **`gemini-2.5-flash-lite`**: **$0.10 / 1M input tokens**, **$0.40 / 1M output tokens** (including thinking tokens).
  - **`gemini-2.5-flash`**: **$0.30 / 1M input tokens**, **$2.50 / 1M output tokens** (including thinking tokens).
  - (Context Caching available for prompts $>32\text{k}$ tokens: 75% discount on cached inputs).
- **Rate Limits & Spend Protections (Tier 1)**:
  - Moving to Paid Tier 1 unlocks higher RPM/TPM and eliminates RPD restrictions.
  - **Spend-based Rate Limit**: To protect against runaway billing loops, Google enforces a **$10 per 10-minute** spend rate limit on Tier 1 accounts.
- **Enterprise Privacy**:
  - Unlike the Free Tier, Paid Tier API calls **are NOT logged or used by Google to train models**.
- **Why it fits Untangle**:
  - `gemini-2.5-flash-lite` at $0.10/$0.40 per 1M is cheaper than GPT-4o-mini ($0.15/$0.60) while providing a 1M token context window.
  - Can ingest an entire 300-page book in a single prompt for approximately **$0.03**.

### Paid Option 3: OpenAI GPT-4o-mini
*The gold standard for reliable structured outputs.*

- **Provider**: OpenAI API ([platform.openai.com](https://platform.openai.com))
- **Pricing**:
  - **$0.15 / 1M input tokens**, **$0.60 / 1M output tokens**.
  - (Batch API: 50% discount $\rightarrow$ $0.075 / $0.30).
- **Why it fits Untangle**:
  - OpenAI's `response_format={"type": "json_schema", "strict": true}` guarantees 100% syntactically valid JSON matching Pydantic schemas. Zero JSON parse errors on entity extraction.
  - Very low latency and high availability.

### Paid Option 4: Claude 3.5 Haiku (Anthropic)
*Top-tier nuance and academic comprehension.*

- **Provider**: Anthropic API ([console.anthropic.com](https://console.anthropic.com))
- **Pricing**:
  - **$0.80 / 1M input tokens**, **$4.00 / 1M output tokens**.
  - (Prompt Caching: $0.08 / 1M cached input; Batch API: $0.40 / $2.00).
- **Why it fits Untangle**:
  - Excels at complex scientific and academic paper parsing where terminology is dense.
  - Prompt caching cuts the cost of repeated few-shot extraction prompts by 90%.

### Paid Option 5: OpenAI `text-embedding-3-small`
*Unbeatable commercial embedding pricing.*

- **Pricing**: **$0.02 / 1M tokens** ($0.00002 per 1k tokens).
- **Details**: 1536 dimensions (can be reduced to 512 via MRL dimensionality reduction with near-zero loss in accuracy).
- **Cost in practice**: Embedding an entire 400-page textbook costs approximately **$0.004 (less than half a cent)**.

---

## 5. Side-by-Side Model Comparison Matrix

| Model | Provider | Free Tier Rate Limits / Quotas | Context Window | JSON Mode Reliability | Speed (tokens/s) | Best Role in Untangle |
|---|---|---|---|---|---|---|
| **Gemini 2.5 Flash-Lite** | Google AI Studio | **FREE** (30 RPM / 250k TPM / 1,500 RPD) | 1,000,000 | 9.8 / 10 | ~200 | High-volume entity & relationship extraction workhorse |
| **Gemini 2.5 Flash** | Google AI Studio | **FREE** (10–15 RPM / 250k TPM / 250–1,500 RPD) | 1,000,000 | 9.9 / 10 | ~160 | Book hierarchy, community summaries, & exam gists |
| **Llama 3.3 70B** | Groq Cloud | **FREE** (30 RPM / 12k TPM / **100k TPD cap**) | 128,000 | 9.2 / 10 | ~350 | **Interactive Regulus chat only** (preserves 100k token/day cap) |
| **Llama 3.1 8B** | Groq Cloud | **FREE** (30 RPM / 20k TPM / **500k TPD cap**) | 128,000 | 8.8 / 10 | ~750 | Fast parallel chunk extraction (if using Groq for ingestion) |
| **Qwen 2.5 14B** | Local (Ollama) | **FREE** ($0, self-hosted, no limits) | 32,000 / 128k | 9.4 / 10 | ~35–60 | Offline local development & extraction |
| **bge-small-en-v1.5** | Local (CPU) | **FREE** ($0, self-hosted, no limits) | 512 | n/a | >1,500 | Dense chunk & entity embeddings (zero API dependency) |
| **DeepSeek-V3** | DeepSeek API | **$0.14 / $0.28 per 1M** (uncapped) | 64,000 | 9.6 / 10 | ~70 | High-reasoning chat & ultra-budget production extraction |
| **GPT-4o-mini** | OpenAI API | **$0.15 / $0.60 per 1M** (uncapped) | 128,000 | 10 / 10 (Strict) | ~110 | Flawless JSON extraction & community summaries |
| **Claude 3.5 Haiku** | Anthropic API | **$0.80 / $4.00 per 1M** (uncapped) | 200,000 | 9.7 / 10 | ~80 | Complex academic paper extraction & eval judge |
| **text-embed-3-small**| OpenAI API | **$0.02 / 1M** ($0.004 / 400-page book) | 8,191 | n/a | Instant | Commercial vector embeddings |

---

## 6. Recommended Architecture Recipes

Depending on your budget, environment, and deployment goals, choose one of these three pre-configured recipes:

### Recipe A: "The 100% Free Tier Stack" *(Recommended for Development & Demos)*
*Zero monthly spend. High daily throughput. Fast interactive chat. Zero API bills.*

```
├── Entity & Relationship Extraction:  Google Gemini 2.5 Flash-Lite (Free Tier, 30 RPM / 1,500 RPD)
├── Study Mode Book Hierarchy:         Google Gemini 2.5 Flash (Free Tier, 1M context window)
├── Community Summarization:           Google Gemini 2.5 Flash (Free Tier)
├── Dense Vector Embeddings:           Local BAAI/bge-small-en-v1.5 (via fastembed, CPU, $0)
├── Regulus Interactive Chat:          Groq Cloud Llama 3.3 70B (350 tokens/s, uses 100k TPD daily quota)
├── High-Yield Exam Gists:             Google Gemini 2.5 Flash (Free Tier)
└── Total Estimated Cost:              $0.00 / month
```
> **Architecture Note**: By delegating extraction to Gemini 2.5 Flash-Lite and reserving Groq 70B exclusively for Regulus chat queries, you will never trigger Groq's 100,000 TPD cap nor Google's RPM limits.

### Recipe B: "The Budget Production Stack" *(Sub-$2.00 / month for High Volume)*
*Enterprise-grade reliability, strict JSON enforcement, near-zero cost.*

```
├── Entity & Relationship Extraction:  OpenAI GPT-4o-mini (Strict JSON schema) or Gemini 2.5 Flash-Lite
├── Community Summarization:           DeepSeek-V3 ($0.14/1M)
├── Dense Vector Embeddings:           OpenAI text-embedding-3-small ($0.02/1M)
├── Regulus Interactive Chat:          DeepSeek-V3 or Gemini 2.5 Flash
├── Multi-Hop Reasoning / Eval Judge:  DeepSeek-R1 (Chain-of-Thought)
└── Total Estimated Cost:              ~$0.50 – $2.00 / month (hundreds of papers)
```

### Recipe C: "The 100% Air-Gapped Local Stack" *(Zero Cloud Dependencies)*
*Runs entirely offline on consumer hardware with 8GB–16GB RAM.*

```
├── Ingestion Extraction & Hierarchy:  Ollama Qwen 2.5 7B (or 14B Instruct)
├── Dense Vector Embeddings:           Local BAAI/bge-small-en-v1.5
├── Regulus Interactive Chat:          Ollama Qwen 2.5 7B (or Llama 3.2 3B for low-spec)
└── Total Estimated Cost:              $0.00 (Self-hosted)
```

---

## 7. Backend Configuration & Implementation Blueprint

Because Groq, DeepSeek, Ollama, and OpenAI all support the **OpenAI API specification**, you can swap between them in `backend/` by simply modifying environment variables.

### Universal LLM Client Configuration (`backend/.env.local` templates):

#### Example 1: Free Tier Setup (Gemini + Groq + Local Embeddings)
```ini
# ── LLM Settings (Free Tier Setup) ───────────────────────────────────
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...

# Groq for ultra-fast chat streaming (Strictly for single-turn interactive chat)
GROQ_API_KEY=gsk_...
GROQ_CHAT_MODEL=llama-3.3-70b-versatile

# Extraction & Ingestion (Free Gemini tier with 1,500 RPD)
EXTRACTION_MODEL=gemini-2.5-flash-lite
SYNTHESIS_MODEL=gemini-2.5-flash

# Local Free Embeddings
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

#### Example 2: Ultra-Budget Production Setup (DeepSeek + OpenAI Embeddings)
```ini
# ── LLM Settings (DeepSeek Setup) ───────────────────────────────────
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

EXTRACTION_MODEL=deepseek-chat
SYNTHESIS_MODEL=deepseek-chat
REASONING_MODEL=deepseek-reasoner

# Embeddings
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
EMBEDDING_MODEL=text-embedding-3-small
```

#### Example 3: 100% Local Ollama Setup
```ini
# ── LLM Settings (Local Ollama Setup) ────────────────────────────────
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
EXTRACTION_MODEL=qwen2.5:7b-instruct
SYNTHESIS_MODEL=qwen2.5:7b-instruct

EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

#### Example 4: Hugging Face Serverless Free Tier Setup (Qwen 2.5 72B / DeepSeek)
```ini
# ── LLM Settings (Hugging Face Serverless Router) ────────────────────
LLM_PROVIDER=huggingface
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxx
HF_BASE_URL=https://router.huggingface.co/hf-inference/v1

# Ingestion workhorse (pair with Gemini Flash for high volume, or Qwen-Coder)
EXTRACTION_MODEL=Qwen/Qwen2.5-Coder-32B-Instruct
# Regulus multi-hop chat guide & exam prep
SYNTHESIS_MODEL=Qwen/Qwen2.5-72B-Instruct
REASONING_MODEL=deepseek-ai/DeepSeek-R1

# Embeddings via Hugging Face
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=BAAI/bge-m3
```

---

## 8. Summary Recommendation

1. **For testing right now ($0 spend)**: 
   - Use **Google Gemini 2.5 Flash-Lite** for high-volume entity/relation extraction (30 RPM, 1,500 RPD).
   - Use **Google Gemini 2.5 Flash** for structural textbook hierarchy, community summaries, and exam gists (1M context window).
   - Reserve **Groq Llama 3.3 70B** *strictly* for the interactive Regulus chat assistant (`<150ms` streaming, staying well within Groq's 100,000 Tokens-Per-Day limit).
2. **For embeddings**: Run `BAAI/bge-small-en-v1.5` locally using Python's `fastembed` library. It requires zero API keys, consumes almost no memory, and produces 384-dimensional vectors in sub-millisecond speeds.
3. **If you have a $5 budget**: Use **DeepSeek-V3** ($0.14/$0.28 per 1M) and **OpenAI `text-embedding-3-small`** ($0.02 per 1M). You can ingest and explore over 250 documents before even spending $1.00.

