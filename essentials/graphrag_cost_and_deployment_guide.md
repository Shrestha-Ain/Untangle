# GraphRAG Explorer — Cost Effectiveness & Deployment Guide

Pricing and free-tier terms below were checked in September 2026. These change often — re-verify before budgeting seriously, but the *methodology* (how to think about cost tradeoffs) stays valid regardless of exact figures.

---

## 1. LLM Cost — The Dominant Variable Cost

This is the cost that actually scales with usage, so it deserves the most rigor. Current per-million-token API rates:

| Model | Input | Output | Batch Input | Batch Output | Cached Input |
|---|---|---|---|---|---|
| Claude Haiku 4.5 | $1.00 | $5.00 | $0.50 | $2.50 | $0.10 |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $1.50 | $7.50 | $0.30 |
| OpenAI `text-embedding-3-small` | $0.02 | n/a | $0.01 | n/a | n/a |
| GPT-4o-mini (comparison) | $0.15 | $0.60 | — | — | — |

Batch processing is a flat 50% discount on both models, and prompt caching cuts *cached* input tokens by roughly 90% versus standard input pricing.

### 1.1 Per-document ingestion cost (worked estimate)

For a ~20-page document (~13,000 tokens raw text), chunked into ~30 chunks of ~500 tokens with overlap:

| Pipeline step | Model | Calls | Input tok/call | Output tok/call | Cost |
|---|---|---|---|---|---|
| Entity/relation extraction | Haiku 4.5 | 30 (one per chunk) | ~1,000 (chunk + system prompt + few-shot) | ~300 | ~$0.075 |
| Entity disambiguation (borderline cases) | Haiku 4.5 | ~15 | ~300 | ~50 | ~$0.008 |
| Community summarization | Haiku 4.5 | ~8 communities | ~800 | ~150 | ~$0.012 |
| Embeddings (chunks + entities) | `text-embedding-3-small` | ~110 items | ~200 avg | n/a | ~$0.0004 |
| **Total per document** | | | | | **~$0.10** |

### 1.2 Per-query cost (worked estimate)

| Step | Model | Input tok | Output tok | Cost |
|---|---|---|---|---|
| Query classification (local/global) | Haiku 4.5 | ~100 | ~10 | ~$0.0001 |
| Answer synthesis | Sonnet 4.6 | ~2,500 (graph facts + chunk excerpts) | ~400 | ~$0.0135 |
| **Total per query** | | | | **~$0.014** |

Swap synthesis to Haiku 4.5 instead of Sonnet if you want to cut this further (~$0.003/query) — reasonable for a demo where you're optimizing for cost over maximum answer quality; use Sonnet if you want your evaluation report to show best-case accuracy numbers.

### 1.3 What this means in practice

Building and demoing this project — say 20 test documents ingested plus 200 queries during development and interview demos — costs roughly **$2 (ingestion) + $3 (queries) ≈ $5 total** in LLM API spend. This is genuinely useful to know: cost is not a real constraint on building this project, and you should say so plainly if asked, rather than hedging. It only becomes a real design conversation once you're reasoning about hypothetical scale (thousands of documents, real user traffic) — which is exactly the right framing for an interview answer: "at demo scale this cost pennies; here's how I'd control cost if this had 10,000 users."

---

## 2. LLM Cost Optimization Techniques

These are the levers, in order of impact for this specific project:

1. **Model tiering (biggest lever)** — cheap/fast model (Haiku) for the high-volume, low-difficulty extraction step; reserve the stronger model (Sonnet) only for final synthesis, which runs once per user question rather than once per chunk. This single decision is why ingestion costs ~$0.10/document instead of ~$0.30+.
2. **Route ingestion through the Batch API** — extraction already runs asynchronously via Celery, so there's no UX cost to using the Batch API's 24-hour turnaround window instead of real-time calls. This is close to a free 50% cost cut with zero downside for this specific pipeline, since users are already watching a progress bar, not waiting synchronously on extraction.
3. **Prompt caching on the static prompt portion** — your extraction system prompt + few-shot example (~400 tokens) is identical across all ~30 chunk-extraction calls per document. Caching it cuts that repeated portion's cost by ~90% after the first call.
4. **Cache repeated queries in Redis** — hash `(question, document_id)` and cache the full response; free for repeated demo questions, meaningful if this ever had real concurrent users asking overlapping things.
5. **Self-hosted open-source embeddings (optional, low priority)** — `bge-small-en-v1.5` via `sentence-transformers` runs free on CPU and would eliminate the ~$0.0004/document embedding cost entirely. Worth naming as an option, but at this project's scale that cost is already negligible — implementing local embedding serving adds real infra complexity (bundling model weights, managing inference) to save fractions of a cent. This is a good "know when *not* to over-engineer" talking point: the honest answer is it's not worth it until embedding volume is orders of magnitude higher.

---

## 3. Infrastructure Cost — Free-Tier Path (portfolio/demo scale)

| Service | Role | Free tier | Gotcha to know |
|---|---|---|---|
| Vercel | Frontend hosting | 100GB bandwidth/month, permanent free Hobby tier | None significant for a portfolio project |
| Render | Backend + Celery worker | 750 instance-hours/month shared per workspace, free Postgres/Redis included | Spins down after 15 min idle, ~1 min cold-start on next request; running 2 always-on services (API + worker) 24/7 exceeds the shared 750-hour pool |
| Neo4j AuraDB Free | Graph database | 200,000 nodes / 400,000 relationships, free forever, no card required | **Auto-pauses after 72 hours of inactivity**, and is deleted if left paused >30 days — you must manually resume it before a demo/interview |
| Qdrant Cloud Free | Vector database | 1 free-forever cluster: 0.5 vCPU, 1GB RAM, 4GB disk | Fine for a handful of documents; watch disk usage if you ingest many large documents |
| Supabase | Postgres (users, docs, jobs, chat) | 500MB storage, ~5GB egress/month, built-in auth | Free projects can pause after a period of inactivity — verify current terms and resume before demos |
| Upstash Redis | Celery broker + pub/sub + cache | ~10K commands/day, small storage cap | Fine for demo-scale traffic; watch command count if you have chatty pub/sub progress updates |

**Total infrastructure cost at this scale: $0/month.** The only real cost is your own time occasionally waking sleeping free-tier services back up.

**Practical advice this actually implies:** the morning of an interview or demo, hit your Neo4j Aura console to resume the instance if paused, and make one warm-up request to your Render backend a few minutes before you need it live — this single habit avoids the single most common "it's not working!" moment in a live demo of a project built entirely on free tiers.

### Worth knowing: GraphRAG-specific alternatives
If Neo4j's node/relationship cap or its pause behavior become annoying, **FalkorDB** is worth investigating — it's explicitly built for GraphRAG-style workloads with a cloud tier aimed at prototypes, and **Memgraph** is Cypher-compatible (near-drop-in for Neo4j) with different free-tier terms. Not necessary for this project's scale, but a reasonable thing to have looked into if asked "what alternatives did you consider?"

---

## 4. Infrastructure Cost — Beyond Free Tier (moderate real usage)

Worth understanding even if you never actually pay for this, because "how would this cost scale" is a very natural interview follow-up.

**What breaks first, roughly in order:**
1. **Render's 750 shared instance-hours** — two always-on services (API + Celery worker) exceed this; next step is Render's Starter tier at roughly $7/service/month (~$14/month for both), or consolidating API and worker into one process for low-traffic scenarios.
2. **Neo4j AuraDB's node/relationship cap** — 200K nodes is generous for a single portfolio demo but would be reached with a large multi-document corpus. The jump to AuraDB Professional is steep — priced per GB of data per month, which can run into the hundreds of dollars monthly for even modest graph sizes.
3. **Qdrant's 1GB RAM cluster** — fine until vector count grows substantially; paid tiers are usage-based infrastructure billing (no per-query fees), with typical moderate workloads running roughly $150-200/month based on current published estimates.

### 4.1 The managed-vs-self-hosted tradeoff (the actual cost-engineering conversation)

This is the single most interview-relevant cost insight in this whole guide: **managed database services are cheap or free at small scale and become disproportionately expensive at moderate scale**, especially Neo4j Aura's per-GB pricing. The alternative is self-hosting the same open-source databases (Neo4j Community Edition, Qdrant, Postgres, Redis) via Docker Compose on a single low-cost VPS (e.g., a $5-20/month Hetzner or DigitalOcean box).

| Approach | Cost at moderate scale | Tradeoff |
|---|---|---|
| Fully managed (Aura + Qdrant Cloud + Render paid tiers) | Roughly $150-300+/month | Zero ops burden — backups, upgrades, scaling handled for you |
| Self-hosted on one VPS via Docker Compose | Roughly $20-40/month total | You own backups, security patching, and manual scaling |

Being able to articulate *why* you'd pick one over the other for a given situation (a funded startup with no ops team → pay for managed; a cost-constrained side project or a team with real infra skill → self-host) is a stronger signal than just knowing the two options exist.

---

## 5. Deployment Methodologies

### 5.1 Local development via Docker Compose
Run all six services (frontend, backend, Celery worker, Postgres, Neo4j, Qdrant, Redis) with one command. For a good dev experience, mount your source directories as volumes so code changes hot-reload without rebuilding the image, and keep a separate `docker-compose.override.yml` for dev-only settings (debug ports exposed, verbose logging) layered on top of a shared base `docker-compose.yml` used in both dev and CI.

### 5.2 Environment strategy
Three environments, minimum: **local** (Docker Compose, `.env.local`), **staging/preview** (optional — Vercel and Render both support preview deployments per pull request automatically), and **production** (`.env.production`, values stored in the platform's secret manager, never in the repo). Keep the *shape* of environment variables identical across environments (same variable names) so promoting a build from staging to prod never requires code changes, only config changes.

### 5.3 Database migrations as part of deploy
Use Alembic for Postgres schema changes. The deploy sequence should always be: **run migrations first, then start the new application version** — never the reverse, or you risk the new code querying a schema that doesn't exist yet. Most platforms (Render, Railway) support a "pre-deploy command" hook for exactly this.

### 5.4 Multi-stage Docker builds
A naive Dockerfile copies your full source tree and installs dependencies in one stage, producing a bloated image. A multi-stage build compiles/installs in one stage, then copies only the final artifacts into a slim runtime image — smaller images mean faster deploys and less usage against free-tier build-minute limits, which matters concretely on Render's free tier (500 build-minutes/month).

### 5.5 CI/CD pipeline (GitHub Actions)

```yaml
name: CI/CD
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: cd backend && ruff check . && pytest

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd frontend && npm ci && npm run type-check && npm run build

  deploy:
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render deploy
        run: curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
      - name: Vercel deploy
        run: echo "Vercel auto-deploys on push to main via its own Git integration — no manual step needed"
```

Note the last step: Vercel's Git integration deploys automatically on push without needing an explicit CI step at all — only Render needs an explicit deploy-hook trigger in this setup.

### 5.6 Health checks
Add a `GET /health` endpoint that checks connectivity to Postgres, Neo4j, and Qdrant (not just "is the process running") and returns per-dependency status. Render and most platforms use this to determine whether a deploy succeeded and whether to route traffic to it — a shallow health check that only confirms "the web server is up" will happily report healthy even when your graph database connection is silently broken.

### 5.7 Secrets management
Never commit `.env` files — add them to `.gitignore` from the very first commit. Store production secrets in the platform's own secret store (Render's environment variable dashboard, Vercel's project settings) rather than in a checked-in config file. Rotate the JWT secret and any API keys if they're ever accidentally exposed (a genuine, non-theoretical risk with student projects pushed to public GitHub repos).

### 5.8 Rollback strategy
At this project's scale, the simplest correct rollback strategy is: keep deploys tied to Git commits, and rolling back means re-deploying the previous commit/tag. You don't need blue-green deployments or canary releases for a portfolio project — but understanding *why* those exist (avoiding downtime during a bad deploy at real traffic scale) is worth being able to explain if asked, even though you'd correctly judge it as over-engineering for this project's actual scale.

---

## 6. Deployment Order of Operations

1. Provision the three managed databases first, independently: Neo4j AuraDB Free, Qdrant Cloud Free, Supabase Postgres, Upstash Redis. Note down all four connection strings.
2. Deploy the backend + Celery worker to Render, wiring in the four connection strings plus your LLM API key as environment variables.
3. Run the initial Alembic migration against the live Supabase Postgres instance (either via a one-off Render job or manually from your machine pointed at the production connection string).
4. Deploy the frontend to Vercel, setting the API base URL environment variable to your live Render backend URL.
5. Smoke test end-to-end: upload a small test document, confirm the WebSocket progress events arrive, confirm a chat query returns a graph-grounded answer.

---

## 7. Monitoring on a Budget

- **Sentry** (free tier) for error tracking on both backend and frontend — catches exceptions you'd otherwise only discover when a demo breaks live.
- **Structured logging** (`structlog` or similar) so Render's log viewer is actually searchable instead of unstructured print statements.
- **UptimeRobot** (free tier) pinging your `/health` endpoint every few minutes — this doubles as a practical fix for Render's 15-minute sleep behavior, since regular pings keep the free service warm during periods you're actively demoing it.

---

## 8. Total Cost of Ownership — Summary

| Scale | Monthly infra cost | Monthly LLM cost | Notes |
|---|---|---|---|
| Building + portfolio demos | $0 | ~$5 total (one-time, not recurring) | Entirely free-tier infra; LLM cost is a rounding error |
| Light real usage (few users) | $0-15 | Usage-dependent, likely single-digit $ | Render Starter tier if you need always-on with no cold starts |
| Moderate real usage | $150-300 (managed) or $20-40 (self-hosted VPS) | Scales with queries; model tiering + caching keep this controlled | This is where the managed-vs-self-hosted conversation becomes real, not hypothetical |

The single best sentence you can say in an interview about this project's cost profile: *"It costs essentially nothing to run at demo scale because of free-tier infrastructure and aggressive model tiering, and I know exactly which three things would need to change first if it had real traffic — and roughly what each of those changes would cost."* That's a genuinely rare thing for a portfolio project to be able to say credibly, and it's a direct result of having done this cost analysis rather than skipping it.
