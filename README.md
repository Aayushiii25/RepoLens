<p align="center">
  <h1 align="center">🔍 RepoLens</h1>
  <p align="center">
    <strong>AI-Powered Open Source Discovery & Contribution Intelligence Platform</strong>
  </p>
  <p align="center">
    The operating system for open-source contributors — discover repositories, understand codebases, evaluate project health, and find the perfect issue to tackle.
  </p>
  <p align="center">
    <a href="#-what-is-repolens">About</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-features">Features</a> •
    <a href="#-tech-stack">Tech Stack</a> •
    <a href="#-getting-started">Getting Started</a> •
    <a href="#-api-reference">API</a> •
    <a href="#-roadmap">Roadmap</a>
  </p>
</p>

---

## 💡 What is RepoLens?

Open source contribution is one of the most valuable ways for developers to grow. But existing tools make it harder than it needs to be:

- GitHub search is keyword-only — no semantic understanding
- Beginners can't tell which repos match their skill level
- "Good first issue" labels are inconsistent and often stale
- Developers spend hours understanding unfamiliar codebases before writing a single line

**RepoLens solves all of this.** It is a full-stack platform that combines a live GitHub GraphQL integration, cache-first backend, and a beautiful workspace UI to give developers a single place to:

1. **Discover** — find repositories by meaning, not just keywords
2. **Understand** — AI summaries, architecture overviews, tech stack detection
3. **Contribute** — recommended issues sorted by difficulty, estimated time, and acceptance rate

---

## 🏗️ Architecture

<a name="-architecture"></a>

### Current Implementation

```
┌──────────────────────────────────────────────────────────────────┐
│                      FRONTEND  (Next.js 15)                      │
│   Command Palette (⌘K)  →  Results  →  Repository Workspace     │
└───────────────────────────────┬──────────────────────────────────┘
                                │  HTTP / REST
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                       BACKEND  (FastAPI)                         │
│                                                                  │
│  GET /api/v1/search?q=react                                      │
│                                                                  │
│  ┌──────────────┐   ┌───────────────────┐                       │
│  │    Router     │──▶│  Search Service   │                       │
│  └──────────────┘   └────────┬──────────┘                       │
│                               │                                  │
│              ┌────────────────┼────────────────┐                │
│              ▼                ▼                ▼                 │
│    ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│    │  TTL Cache   │  │   Database   │  │  GitHub GraphQL API │  │
│    │ (In-Memory)  │  │  (SQLite)    │  │  (Authenticated)    │  │
│    │   5-min TTL  │  │  Upsert-on-  │  │                     │  │
│    │              │  │  write       │  │                     │  │
│    └──────────────┘  └──────────────┘  └─────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Target Architecture (Roadmap)

```
                    ┌─────────────────────────────────────┐
                    │        Next.js Frontend              │
                    │  Dashboard • Search • Profile        │
                    └────────────────┬────────────────────┘
                                     │ REST + WebSocket
                                     ▼
                    ┌────────────────────────────────────────┐
                    │          API Gateway (FastAPI)          │
                    └────────┬──────────────┬────────────────┘
                             │              │              │
               ┌─────────────┘   ┌──────────┘   ┌─────────┘
               ▼                  ▼               ▼
      Search Service     Recommendation     Analytics Service
               │             Service               │
               ▼                  │               ▼
          Qdrant DB         ML Inference       PostgreSQL
               │              (XGBoost)
               ▼
      Embedding Service
      (Sentence Transformers)
               │
               ▼
      Feature Store + MLflow
```

**Key architectural decisions:**

| Decision | Rationale |
|---|---|
| **Cache-first reads** | Subsequent identical searches return in <50ms instead of ~1s from GitHub |
| **Upsert-on-write** | Every GitHub response is persisted — builds a local knowledge base over time |
| **GraphQL over REST** | Fetch exactly the needed fields in one request — no over-fetching |
| **Async I/O** | `httpx.AsyncClient` for non-blocking GitHub calls under load |
| **Clean DTO pattern** | Frontend never sees raw GitHub responses — service layer transforms everything |
| **LLM Gateway** (planned) | Single point for all AI calls — prompt management, caching, model routing |

---

## ✨ Features

<a name="-features"></a>

### ✅ Implemented

| Feature | Description |
|---|---|
| 🔎 **Live GitHub Search** | Real-time search via GitHub GraphQL API with 400ms debounce |
| ⚡ **Command Palette** | `Ctrl+K` / `⌘K` global search with full keyboard navigation |
| 🏥 **Repository Health Score** | Activity, Security, Community, Documentation, Maintainability metrics |
| 🧱 **Tech Stack Detection** | Auto-detected technology badges per repository |
| 📊 **Recommended Issues** | Table with difficulty, estimated time, and acceptance rate |
| 🕐 **Recent & Trending** | Persisted localStorage search history + curated trending terms |
| 💀 **Skeleton Loading** | Animated skeleton states — no spinners, no frozen pages |
| 🎨 **Dual Theme** | Dark (golden glow) + Light (blood-red aesthetic), fully responsive |
| 🏛️ **3-Column Workspace** | GitHub + Linear + VS Code inspired layout with sticky sidebars |
| 🗄️ **Cache + DB Layer** | Search results cached 5 min, persisted to SQLite via SQLAlchemy |
| 📡 **REST API** | `GET /api/v1/search` with Swagger docs at `/docs` |

### 🔮 Planned (per Roadmap)

| Feature | Sprint |
|---|---|
| 🧠 Semantic search (Qdrant + Sentence Transformers) | Sprint 3 |
| 🤖 AI-powered repository summaries (LLM Gateway) | Sprint 6 |
| 📈 Analytics dashboard (stars, contributor trends) | Sprint 4 |
| 🔐 GitHub OAuth + user profiles | Sprint 2 |
| 💬 Repository Chat (RAG over README + code) | Sprint 6 |
| 🎓 Contribution Coach — step-by-step guidance | Sprint 7 |
| 📦 Docker Compose (Postgres + Redis + Qdrant) | Sprint 1 |
| 🌐 VS Code extension, Slack/Discord bot | Future |

---

## 🛠️ Tech Stack

<a name="-tech-stack"></a>

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 15** | React framework, App Router, Server Components |
| **TypeScript** | Type-safe development end-to-end |
| **Tailwind CSS** | Utility-first styling |
| **shadcn/ui** | Accessible, composable UI component library |
| **cmdk** | Keyboard-first command palette |
| **next-themes** | Dark/light mode management |
| **TanStack Query** | Server state management (planned) |
| **Zustand** | UI state (planned) |

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | Async Python web framework |
| **SQLAlchemy 2** | ORM with async support (SQLite now → PostgreSQL ready) |
| **httpx** | Async HTTP client for GitHub GraphQL calls |
| **Pydantic v2** | Request/response validation and serialization |
| **In-Memory Cache** | TTL-based caching (Redis-compatible interface, trivial to swap) |
| **Celery + Redis** | Background jobs — embedding generation, GitHub sync (planned) |

### AI / ML (Planned)
| Technology | Purpose |
|---|---|
| **Qdrant** | Vector database for semantic search |
| **Sentence Transformers** | Text embeddings (all-MiniLM / bge-small) |
| **XGBoost** | Repository health prediction model |
| **MLflow** | ML experiment tracking + model registry |
| **Hybrid Ranking** | BM25 keyword + vector search + cross-encoder re-ranking |

### APIs & Infrastructure
| Technology | Purpose |
|---|---|
| **GitHub GraphQL API** | Repository data, issues, contributors |
| **Docker / Docker Compose** | Local service orchestration |
| **Vercel** | Frontend deployment |
| **Kubernetes** | Production backend deployment (planned) |
| **Prometheus + Grafana** | Monitoring (planned) |

---

## 🚀 Getting Started

<a name="-getting-started"></a>

### Prerequisites
- **Node.js** ≥ 18
- **Python** ≥ 3.11
- **GitHub Personal Access Token** — [Generate here](https://github.com/settings/tokens) (Classic, `public_repo` scope)

### 1. Clone

```bash
git clone https://github.com/Aayushiii25/RepoLens.git
cd RepoLens
```

### 2. Start the Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env .env.local
# Edit .env and set GITHUB_TOKEN=ghp_your_token_here

# Run
uvicorn app.main:app --reload --port 8000
```

📄 Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

🌐 App: [http://localhost:3002](http://localhost:3002)

### 4. Test It

Press `Ctrl+K` and type `react` — you'll get live repository results from GitHub, cached and persisted automatically.

---

## 📁 Project Structure

```
RepoLens/
├── frontend/                         # Next.js 15 application
│   └── src/
│       ├── app/                      # App Router (route groups: dashboard, auth)
│       ├── components/
│       │   ├── layout/               # AppShell, Navbar, Sidebar, PageContainer
│       │   └── ui/                   # shadcn/ui components
│       ├── features/
│       │   ├── repository/           # Repository workspace (Header, Tabs, Health, Issues)
│       │   └── search/               # Command palette, suggestions, recent searches
│       ├── services/                 # API client layer (search.ts)
│       ├── hooks/                    # Custom React hooks
│       ├── data/                     # Static data (trending searches)
│       └── types/                    # Shared TypeScript types
│
├── backend/                          # FastAPI application
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py             # pydantic-settings config loader
│   │   │   └── cache.py              # In-memory TTL cache (Redis-compatible)
│   │   ├── db/
│   │   │   └── session.py            # SQLAlchemy engine + session factory
│   │   ├── github/
│   │   │   └── client.py             # Async GraphQL client (singleton)
│   │   ├── models/
│   │   │   └── repository.py         # SQLAlchemy Repository model
│   │   ├── search/
│   │   │   ├── router.py             # GET /api/v1/search
│   │   │   ├── service.py            # Cache → GitHub → DB → Cache logic
│   │   │   └── schemas.py            # Pydantic DTOs
│   │   └── main.py                   # FastAPI app, CORS, lifespan
│   ├── docker/
│   │   └── docker-compose.yml        # Postgres + Redis for production
│   ├── requirements.txt
│   └── .env
│
└── README.md
```

---

## 📡 API Reference

<a name="-api-reference"></a>

### `GET /api/v1/search?q={query}`

Search GitHub repositories with caching.

**Query Params:**
| Param | Type | Required | Description |
|---|---|---|---|
| `q` | string | ✅ | Search query (min 1 char) |

**Response:**
```json
{
  "query": "react",
  "count": 20,
  "cached": false,
  "results": [
    {
      "id": 1,
      "full_name": "facebook/react",
      "owner": "facebook",
      "name": "react",
      "description": "The library for web and native user interfaces.",
      "language": "JavaScript",
      "stars": 232000,
      "forks": 47400,
      "open_issues": 940,
      "topics": ["javascript", "frontend", "react"],
      "license": "MIT",
      "default_branch": "main",
      "updated_at": "2026-06-29T10:00:00Z"
    }
  ]
}
```

**Caching behaviour:**
- First call: ~1s (GitHub GraphQL)
- Subsequent calls (within 5 min): <50ms (in-memory cache)
- All results upserted to SQLite for persistence

### Planned Endpoints

```
GET  /api/v1/repositories/{id}             Repository details + health
GET  /api/v1/repositories/{id}/health      Health score breakdown
GET  /api/v1/repositories/{id}/similar     Similar repositories
POST /api/v1/search/semantic               Natural language search (Qdrant)
POST /api/v1/recommendations/repositories  Skill-based repo suggestions
POST /api/v1/recommendations/issues        Issue recommendations by difficulty
POST /api/v1/ai/explain                    AI summary of a repository
POST /api/v1/ai/contribution-coach         Step-by-step contribution guidance
GET  /api/v1/repositories/trending         Trending repositories
```

---

## 🧠 Engineering Highlights

| Pattern | Implementation |
|---|---|
| **Cache-First** | Read from cache first (TTL 5 min), fallback to GitHub on miss |
| **Upsert-on-Write** | `INSERT ... ON CONFLICT DO UPDATE` — no duplicates, always fresh |
| **GraphQL over REST** | Single request for 12 fields — stars, forks, language, topics, license, issues, branch |
| **Debounced Search** | 400ms debounce in frontend prevents API floods while typing |
| **DTO Pattern** | Raw GitHub responses never reach the frontend — Pydantic models as contract |
| **Singleton Client** | One `httpx.AsyncClient` for all GitHub calls — connection pooling, shared auth |
| **Lifespan Events** | DB tables auto-created on startup, GitHub client gracefully closed on shutdown |
| **Feature-First Structure** | Frontend organized by `features/repository` and `features/search` — scales cleanly |

---

## 📈 Roadmap

<a name="-roadmap"></a>

Based on the full sprint plan:

```
Sprint 1  ✅  FastAPI + Next.js foundation
Sprint 2  ✅  Repository workspace, command palette, search UI
Sprint 3  ✅  Live GitHub search + cache-first backend
Sprint 4  🔄  Semantic search (Qdrant), repository details + charts
Sprint 5  ⬜  Repository health engine, recommendation engine
Sprint 6  ⬜  AI summaries (LLM Gateway), repository chat (RAG)
Sprint 7  ⬜  Contribution Coach, progress tracking
Sprint 8  ⬜  Testing, performance, production deployment
```

**Performance targets:**
- Search latency: **< 300ms**
- Recommendation latency: **< 500ms**
- API availability: **99.9%**
- Scale: **5M+ repositories, 100M+ issues**

---

## 🤝 Contributing

This project is actively developed. The architecture is designed to grow from a working MVP toward a production-grade ML platform.

To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit your changes (`git commit -m "feat: add ..."`)
4. Push and open a Pull Request

---

## 👤 Author

**Aayushi Dhurandhar**

- GitHub: [@Aayushiii25](https://github.com/Aayushiii25)

---

<p align="center">
  <em>Built with Next.js, FastAPI, and the GitHub GraphQL API</em><br/>
  <em>"The operating system for open-source contributors."</em>
</p>
