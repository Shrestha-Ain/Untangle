# Untangle — GraphRAG Knowledge Mapping Tool

Turn research papers and textbooks into interactive, explorable knowledge maps. Upload academic material, watch it get transformed into an isometric map of entities, topics, and their relationships, and query it through **Regulus**, an AI guide that reasons across the graph and highlights exactly what it used to answer.

**Stack:** Vue 3 · TypeScript · Vite · Tailwind CSS · FastAPI · Neo4j · PostgreSQL · Qdrant · Redis · Celery · Clerk

**Two modes:**
- **Research Mode** — Papers → entity/relationship/community knowledge maps
- **Study Mode** — Books/textbooks → chapter → section → topic hierarchy maps

---

## Prerequisites

| Tool | Min Version | Check |
|---|---|---|
| Python | 3.13+ | `python --version` |
| uv | any | `uv --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |

Install `uv` if you don't have it:
```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Backend Setup (FastAPI + uv)

```bash
cd backend
uv venv
uv sync
cp .env.example .env
```

Open `.env` and fill in:

```env
# Database connections
DATABASE_URL=postgresql://user:password@localhost:5432/untangle
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
QDRANT_URL=http://localhost:6333

# Redis / Celery
REDIS_URL=redis://localhost:6379/0

# Clerk (backend JWT verification)
CLERK_SECRET_KEY=sk_test_...

# LLM API (use at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

```bash
# Start the FastAPI dev server
uv run uvicorn app.main:app --reload --port 8000

# (Separate terminal) Start the Celery worker
uv run celery -A app.core.celery_app worker --loglevel=info
```

API: **http://localhost:8000**  
Docs: **http://localhost:8000/docs**

> `uv run <command>` always uses the project's `.venv` — no manual activation needed.

---

## Frontend Setup (Vue 3 + Vite + Tailwind)

```bash
cd frontend
npm install
cp .env.example .env.local
```

Open `frontend/.env.local` and set:

```env
VITE_API_URL=http://localhost:8000
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

```bash
npm run dev
```

Frontend: **http://localhost:5173**

> In development, Vite proxies `/api/*` → `http://localhost:8000` and `/ws/*` → `ws://localhost:8000`. No CORS issues locally.

---

## Running Both Together

```bash
# Terminal 1
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

Open **http://localhost:5173**, sign in with Clerk, and upload your first document.

---

## Useful Commands

### Backend
```bash
uv run pytest              # run tests
uv run ruff check .        # lint
uv run ruff format .       # format
uv add <package>           # add dependency
uv add --dev <package>     # add dev dependency
```

### Frontend
```bash
npm run build              # production build
npm run preview            # preview production build locally
npx vue-tsc --noEmit       # type-check without building
```

---

## Challenges Faced and How to Fix Them

### 1. Clock Skew / Out-of-Sync System Clock Causing Clerk JWT Failures (`401 Unauthorized`)

- **Symptom:**
  - After signing in via Clerk (e.g., Google OAuth or email), the UI continues showing `"Local Dev"` badge or fails to connect to the backend.
  - The backend logs `401 Unauthorized` on `GET /api/v1/auth/me` and other protected endpoints.
  - Token verification fails with `Token has expired` or signature rejection even immediately after logging in.

- **Root Cause:**
  - JWT tokens issued by Clerk include standard timestamp claims (`iat` for "Issued At" and `exp` for "Expiration").
  - If your local operating system clock drifts or is out of sync with internet standard time (NTP), `jwt.decode` on the backend validates the token timestamps against the local host machine's system time. A drifted clock causes immediate rejection of valid tokens.

- **How to Fix:**
  - **Windows:**
    1. Open **Settings** &rarr; **Time & Language** &rarr; **Date & Time**.
    2. Toggle **"Set time automatically"** to **On**.
    3. Click the **"Sync now"** button under *Additional settings*.
    4. Alternatively, open PowerShell as Administrator and run:
       ```powershell
       w32tm /resync
       ```
  - **macOS / Linux:**
    - On macOS:
      ```bash
      sudo sntp -sS time.apple.com
      ```
    - On Linux:
      ```bash
      sudo systemctl restart systemd-timesyncd
      # or
      sudo chronyd -q 'server pool.ntp.org iburst'
      ```
  - After re-synchronizing your system clock, hard refresh the browser (`Ctrl+Shift+R` or `Cmd+Shift+R`) and sign in again.

### 2. Google OAuth JWT `at_hash` Validation

- **Symptom:** Backend returns `401 Unauthorized` with `Invalid token: No access_token provided` during token decoding for users signing in through Google.
- **Root Cause:** Tokens issued via Google OAuth include an `at_hash` (access token hash) claim. By default, `python-jose` expects an `access_token` parameter when `verify_at_hash` is enabled.
- **How to Fix:** In `backend/app/core/security.py`, pass `"verify_at_hash": False` in the `jwt.decode()` options.