# RepoLens

**AI-Powered Open Source Discovery and Contribution Intelligence Platform**

RepoLens helps developers discover high-quality open-source repositories, evaluate repository health, understand codebases, and find meaningful contribution opportunities — powered by the GitHub GraphQL API, a cache-first backend, and a planned semantic search engine.

---

## Problem Statement

Open-source contribution is one of the most effective ways for developers to grow. Existing tools fail in several ways:

- Repository discovery relies entirely on keyword matching
- Beginners cannot determine which repositories match their skill level
- "Good first issue" labels are inconsistent and frequently outdated
- Developers spend hours reading unfamiliar codebases before contributing
- Repository health and long-term sustainability are difficult to assess

RepoLens addresses all of these problems in a single, unified developer workspace.

---

## System Architecture

```
                    +---------------------------------------------+
                    |           Next.js 15  (Frontend)            |
                    |                                             |
                    |   Command Palette   Repository Workspace    |
                    |   Search Results    Health Dashboard        |
                    +---------------------+-----------------------+
                                          |
                                   REST / WebSocket
                                          |
                    +---------------------v-----------------------+
                    |          API Gateway  (FastAPI)             |
                    +--------+-------------+-------------+--------+
                             |             |             |
               +-------------+   +---------+   +---------+---------+
               |             |   |         |   |                   |
               v             |   v         |   v                   |
     Search Service          | Recommend   |  Analytics            |
               |             |  Service    |  Service              |
               v             |             |                       |
          Qdrant DB          |  ML Models  |  PostgreSQL           |
               |             |  (XGBoost)  |                       |
               v             |             |                       |
    Embedding Service        +------+------+                       |
    (Sentence Transformers)         |                              |
               |              Feature Store                        |
               v              (Feast + MLflow)                     |
       Hybrid Ranker                                               |
    (BM25 + Vector + Cross                                         |
         Encoder)                                                  |
               |                                                   |
               v                                                   |
     Top Repository Results  <-------------------------------+-----+
               |                         Redis Cache         |
               +-------------------------------------------->+
```

### Current Implementation

```
     Browser
        |
        | Ctrl+K
        v
  Command Palette  (cmdk, Next.js)
        |
        | debounced 400ms
        v
  GET /api/v1/search?q=react
        |
        v
  +-----+-----+
  |           |
  v           v
Cache      GitHub GraphQL API
(TTL 5m)   (httpx async client)
  |           |
  |           v
  |      Transform response
  |      (DTO pattern)
  |           |
  |           v
  |       SQLite DB
  |       (upsert-on-write)
  |           |
  +-----+-----+
        |
        v
   JSON Response
        |
        v
  Repository Result Cards
```

---

## Data Flow

```
User Types Query
      |
      v
 400ms Debounce  (frontend)
      |
      v
 Cache Lookup
      |
    Hit?
   /    \
 YES     NO
  |       |
  v       v
Return  GitHub GraphQL API
 (<50ms)      |
              v
       Parse + Validate
       (Pydantic v2)
              |
              v
       Upsert to Database
       (update if exists)
              |
              v
       Write to Cache
       (5 min TTL)
              |
              v
       Return to Frontend
```

---

## Semantic Search Pipeline (Planned)

```
User Query: "distributed backend in Go using Redis"
      |
      v
 Embedding Model
 (all-MiniLM-L6-v2 / bge-small-en)
      |
      v
 Qdrant Vector Search  (semantic similarity)
      |
      v
 BM25 Keyword Search  (exact term matching)
      |
      v
 Hybrid Fusion (RRF scoring)
      |
      v
 Cross Encoder Re-ranking
      |
      v
 Top 20 Repositories
```

This hybrid pipeline gives significantly better relevance than keyword search alone. A query like *"distributed backend in Go"* will surface repositories that do not explicitly contain those words but are semantically similar.

---

## Repository Health Engine (Planned)

```
Repository
    |
    +----------+----------+----------+----------+
    |          |          |          |          |
    v          v          v          v          v
 Commits    Issues    Pull Req   Releases  Contributors
    |          |          |          |          |
    +----------+----------+----------+----------+
                          |
                          v
                  Feature Engineering
                          |
                          v
               Health Prediction Model (XGBoost)
                          |
                          v
              +------+--------+-------+--------+------+
              |      |        |       |        |      |
              v      v        v       v        v      v
          Overall  Activity Security Comm    Docs  Maint.
           Score   Score    Score   Score   Score  Score
              |
              v
         Health Dashboard
```

---

## Recommendation Engine (Planned)

```
Developer Profile
    |
    +---------------+
    |               |
    v               v
Programming      Contribution
Languages        History
    |               |
    +-------+-------+
            |
            v
   Semantic Matching
   (embeddings + cosine similarity)
            |
            v
   Collaborative Filtering
   (users with similar skills liked...)
            |
            v
   Repository Ranking
   + Issue Ranking
            |
            v
   Personalized
   Contribution Roadmap
```

---

## AI Gateway Architecture (Planned)

```
   AI Summary
       |
 Issue Explanation
       |
 Repository Q&A
       |
Contribution Coach
       |
       v
 +------------------+
 |   LLM Gateway    |
 |                  |
 | Prompt Templates |
 | Response Cache   |
 | Rate Limiting    |
 | Model Routing    |
 +--------+---------+
          |
    +-----+------+
    |             |
    v             v
 OpenAI        Gemini
              (or Ollama
              for local)
```

A single gateway handles all AI calls. Swapping models, managing prompts, and controlling costs all happen in one place.

---

## Database Schema

```
Users
  id, github_id, username, email, avatar_url, bio

    |
    +-------------------+--------------------+
    |                   |                    |
    v                   v                    v
SavedRepositories   SavedSearches       UserSkills
  user_id             user_id, query,     user_id, skill,
  repository_id       filters             level, years_exp

Repositories
  id, github_repo_id, full_name, owner, description
  primary_language, license, stars, forks, open_issues
  topics (JSONB), created_at, updated_at, last_commit_at

    |
    +----------+----------+----------+
    |          |          |          |
    v          v          v          v
Contributors  Issues   PullReqs   Releases
  repo_id     repo_id   repo_id    repo_id
  username    title     title      tag
  avatar      state     merged     published_at
  contribs    labels    merge_time download_count
              diff.     review_ct

RepositoryMetrics  (historical, powers charts)
  repo_id, date, stars, forks, commits, issues, prs

HealthScores
  repo_id, overall, activity_score, security_score
  community_score, documentation_score, maintainability_score

Recommendations
  user_id, repo_id, match_score, reason

RepositorySummaries  (LLM output cache)
  repo_id, summary, architecture, difficulty, learning_outcomes

IssueRecommendations
  user_id, issue_id, score, estimated_time
```

**Vector Database (Qdrant)**

```
Collection: repository_embeddings

Payload per record:
  {
    "repo_id": 124,
    "name": "CloudQuery",
    "language": "Go",
    "topics": ["etl", "cloud", "postgres"],
    "stars": 14321
  }

Vector: 768 dimensions
Generated from: README + description + topics + tech stack
```

---

## Tech Stack

**Frontend**

| Technology | Purpose |
|---|---|
| Next.js 15 | React framework, App Router |
| TypeScript | Type safety across the codebase |
| Tailwind CSS | Utility-first styling |
| shadcn/ui | Accessible component library |
| cmdk | Command palette with full keyboard navigation |
| TanStack Query | Server state management |
| Zustand | UI state |

**Backend**

| Technology | Purpose |
|---|---|
| FastAPI | Async Python web framework |
| SQLAlchemy 2 | ORM, currently SQLite, ready to swap to PostgreSQL |
| httpx | Async HTTP client for GitHub GraphQL |
| Pydantic v2 | Request / response validation |
| Celery | Background jobs — embeddings, health scoring, GitHub sync |
| Redis | Cache + task queue |

**AI and ML**

| Technology | Purpose |
|---|---|
| Qdrant | Vector database for semantic search |
| Sentence Transformers | Text embedding models |
| XGBoost | Repository health prediction |
| MLflow | Experiment tracking, model registry |

**Infrastructure**

| Technology | Purpose |
|---|---|
| Docker Compose | Local service orchestration |
| Vercel | Frontend deployment |
| GitHub Actions | CI/CD pipeline |
| Kubernetes | Production backend deployment |
| Nginx | Reverse proxy |

---

## Project Structure

```
RepoLens/
|
+-- frontend/
|   +-- src/
|       +-- app/                    App Router route groups
|       |   +-- (dashboard)/        Main workspace
|       |   +-- (auth)/             Login / OAuth
|       |
|       +-- components/
|       |   +-- layout/             AppShell, Navbar, Sidebar
|       |   +-- ui/                 shadcn components
|       |
|       +-- features/
|       |   +-- repository/         Repository workspace
|       |   |   +-- RepositoryHeader.tsx
|       |   |   +-- RepositoryHealth.tsx
|       |   |   +-- RepositoryTabs.tsx
|       |   |   +-- RecommendedIssues.tsx
|       |   |   +-- TechStack.tsx
|       |   |   +-- RepositorySidebar.tsx
|       |   |
|       |   +-- search/             Command palette
|       |       +-- GlobalSearch.tsx
|       |       +-- SearchResultRow.tsx
|       |       +-- RecentSearches.tsx
|       |       +-- SearchTabs.tsx
|       |
|       +-- services/               API client layer
|       +-- hooks/                  Custom React hooks
|       +-- types/                  Shared TypeScript types
|
+-- backend/
    +-- app/
    |   +-- core/
    |   |   +-- config.py           pydantic-settings, loads .env
    |   |   +-- cache.py            TTL cache (Redis-compatible interface)
    |   |
    |   +-- db/
    |   |   +-- session.py          SQLAlchemy engine + session factory
    |   |
    |   +-- github/
    |   |   +-- client.py           Async GraphQL client singleton
    |   |
    |   +-- models/
    |   |   +-- repository.py       SQLAlchemy ORM model
    |   |
    |   +-- search/
    |   |   +-- router.py           GET /api/v1/search
    |   |   +-- service.py          Cache first logic
    |   |   +-- schemas.py          Pydantic DTOs
    |   |
    |   +-- main.py                 App entrypoint, CORS, lifespan
    |
    +-- docker/
    |   +-- docker-compose.yml      Postgres + Redis
    |
    +-- requirements.txt
```

---

## API Reference

### GET /api/v1/search

Search GitHub repositories.

Query parameters:

| Parameter | Type | Required | Description |
|---|---|---|---|
| q | string | yes | Search query |
| language | string | no | Filter by language |
| minStars | integer | no | Minimum stars |

Response:

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
      "description": "The library for web and native user interfaces.",
      "language": "JavaScript",
      "stars": 232000,
      "forks": 47400,
      "open_issues": 940,
      "topics": ["javascript", "frontend", "react"],
      "license": "MIT",
      "updated_at": "2026-06-29T10:00:00Z"
    }
  ]
}
```

**Caching behaviour:**
- First request: ~1 second (GitHub GraphQL)
- Repeat request within 5 minutes: under 50ms (cache hit)

### Planned Endpoints

```
GET  /api/v1/repositories/{id}              Full repository details
GET  /api/v1/repositories/{id}/health       Health score breakdown
GET  /api/v1/repositories/{id}/similar      Similar repositories
GET  /api/v1/repositories/trending          Trending repositories
POST /api/v1/search/semantic                Natural language search
POST /api/v1/recommendations/repositories   Skill-based repo suggestions
POST /api/v1/recommendations/issues         Issue recommendations
POST /api/v1/ai/explain                     Repository AI summary
POST /api/v1/ai/contribution-coach          Step-by-step contribution guide
POST /api/v1/repositories/compare          Compare multiple repositories
POST /api/v1/repositories/{id}/chat         RAG-powered repository Q&A
```

---

## Deployment Architecture

```
          Internet
              |
              v
      Nginx  (reverse proxy)
              |
              v
      FastAPI Gateway
              |
   +----------+----------+
   |          |          |
   v          v          v
Search     Recommend   Analytics
Service    Service     Service
   |          |          |
   v          v          v
PostgreSQL  Qdrant    Redis
            (vectors)  (cache)
              |
              v
           ML Models
           (XGBoost, LLM Gateway)
```

**Scaling strategy:**

| Layer | Approach |
|---|---|
| Frontend | Vercel CDN |
| API | Horizontal FastAPI instances behind Nginx |
| Database | PostgreSQL with read replicas and indexing |
| Search | Distributed Qdrant cluster |
| ML | Separate inference service |
| Cache | Redis with eviction policy |
| Background Jobs | Celery with RabbitMQ |
| Monitoring | Prometheus + Grafana |

---

## Performance Targets

| Metric | Target |
|---|---|
| Search latency | < 300ms |
| Recommendation latency | < 500ms |
| API availability | 99.9% |
| Repository coverage | 5M+ repositories |
| Issue coverage | 100M+ issues |

---

## Engineering Decisions

**GraphQL over REST for GitHub**

A single GraphQL query fetches all 12 required fields in one round trip. The REST API would require multiple requests for the same data.

**Cache-first reads**

Every search checks the in-memory cache before hitting GitHub. First request takes ~1s. All subsequent requests for the same query within 5 minutes return in under 50ms. This also protects against GitHub rate limits.

**Upsert-on-write**

Every GitHub response is written to the database using an update-if-exists pattern. Over time, the local database becomes a rich knowledge base that can power recommendations without calling GitHub at all.

**Async I/O throughout**

The GitHub client uses `httpx.AsyncClient`. The FastAPI endpoints are `async`. The database layer uses SQLAlchemy in non-blocking mode. The system can handle concurrent requests without thread contention.

**DTO pattern**

Raw GitHub responses are transformed by the service layer into typed Pydantic models before reaching the router. The frontend never receives unprocessed third-party API data.

**LLM Gateway**

Rather than allowing individual services to call LLM providers directly, all AI calls route through a single gateway. This provides centralized prompt management, response caching, rate limiting, and the ability to swap models without touching application code.

---

## Local Setup

**Prerequisites**

- Node.js 18 or higher
- Python 3.11 or higher
- GitHub Personal Access Token (classic, public_repo scope)

**Backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# Add your token to .env
echo "GITHUB_TOKEN=ghp_your_token" > .env
echo "DATABASE_URL=sqlite:///./repolens.db" >> .env

uvicorn app.main:app --reload --port 8000
```

Swagger docs: http://localhost:8000/docs

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:3002

---

## Author

Aayushi Dhurandhar

GitHub: https://github.com/Aayushiii25
