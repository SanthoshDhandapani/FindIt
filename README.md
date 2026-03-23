# E-Commerce search engine

An intelligent product search system built as a **Capstone Project 2 (Multimodal Product Search using Vector DBs)** implementation. The system uses CrewAI multi-agent orchestration, Pinecone vector DB, and hybrid semantic + keyword retrieval to deliver ranked, relevancy-scored product results from natural language queries.

Phase 1 covers full text-based search. Phase 2 extends it to image queries (CLIP) and voice queries (Whisper).

---

## Purpose

Standard e-commerce search relies on keyword matching — if you search "comfortable running shoes" and the product is titled "Nike Air Max 270", it may not surface at all. This system solves that by:

- Understanding **user intent** (brand, color, price, sort preference) from natural language
- Running **hybrid retrieval** — combining semantic similarity with keyword relevance
- **Re-ranking results** using a cross-encoder model that blends similarity, product ratings, and review count into a single 0–1 relevancy score
- Tracking **5 measurable KPIs** aligned to the project specification

---

## Categories

| Category | Subcategories |
|---|---|
| Electronics | Laptops, Displays |
| Shoes | Brand-specific with characteristics (color, type, material) |
| Stationery | Notebooks, Water bottles, Pencils |

---

## System architecture

See [`architecture.html`](architecture.html) for the full interactive architecture reference — open it in any browser.

### Layers at a glance

```
┌─────────────────────────────────────────────┐
│  Layer 1 — React search UI                  │
│  Text query · filters · results grid        │
└──────────────────┬──────────────────────────┘
                   │ POST /api/v1/search
┌──────────────────▼──────────────────────────┐
│  Layer 2 — CrewAI agents                    │
│  A1 Query Analyst → A2 Search Strategist    │
│               → A3 Results Ranker           │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  Layer 3 — Core services                    │
│  Hybrid search (RRF) · Embedding service    │
│  Reranker · Ingestion pipeline · FastAPI    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  Layer 4 — Storage                          │
│  Pinecone (vectors) · PostgreSQL (catalog)  │
│  Redis (query cache)                        │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  Layer 5 — Observability & deployment       │
│  LangSmith · Prometheus/Grafana             │
│  Docker + GitHub Actions → AWS ECS          │
└─────────────────────────────────────────────┘
```

---

## Agent pipeline

The three CrewAI agents run sequentially on every search request:

### Agent 1 — Query analyst
Converts raw user text into a structured `ParsedIntent` using `gpt-4o-mini` with a JSON output schema.

**Input:** `"red Nike shoes under ₹5000 high rated"`

**Output:**
```json
{
  "category": "shoes",
  "brand": "Nike",
  "color": "red",
  "price_max": 5000,
  "sort_by": "rating",
  "specificity": "medium"
}
```

### Agent 2 — Search strategist
Decides the optimal search mode by setting `alpha` (semantic/keyword blend weight) and building Pinecone metadata filters.

| Query specificity | Alpha | Search mode |
|---|---|---|
| High (exact model name) | 0.2 | Keyword-heavy |
| Medium (mixed) | 0.6 | Balanced hybrid |
| Low (vague/descriptive) | 0.85 | Semantic-heavy |

Also routes the query to the correct Pinecone namespace and sets `top_k` (20–50 candidates for the ranker to narrow down).

### Agent 3 — Results ranker
Re-scores Pinecone candidates using a cross-encoder model, then blends with product rating and review count.

**Scoring formula:**
```
relevancy = (1 - α) × similarity + α × (rating / 5) + review_boost
review_boost = min(review_count / 1000, 1.0) × 0.05
```

---

## Hybrid search — how it works

Two parallel retrieval strategies are run and merged using **Reciprocal Rank Fusion (RRF)**:

1. **Semantic path** — query text is embedded → cosine similarity search in Pinecone
2. **Keyword path** — BM25 tf-idf scoring on product name + description fields

**RRF merge formula:**
```
score = α × (1 / (k + sem_rank)) + (1 - α) × (1 / (k + kw_rank))
```
where `k = 60` (damping constant) and `α` comes from the Search Strategist.

> To enable true sparse BM25 in Pinecone, upgrade to a sparse-dense hybrid index. The starter template simulates keyword ranking via token overlap scoring.

---

## Metrics (KPIs)

These five metrics are tracked in Prometheus and visualised in Grafana, per project requirements:

| Metric | What it measures | Where instrumented |
|---|---|---|
| Search relevancy score | Avg cross-encoder score per result | Results ranker agent |
| Click-through rate | Clicks ÷ impressions per session | `click_events` table + FastAPI middleware |
| Query processing time | p50 / p95 latency in ms | FastAPI request timer middleware |
| Index update latency | Time from PostgreSQL write → Pinecone confirm | Ingestion pipeline |
| Cache hit rate | Redis hits ÷ total requests | Redis middleware |

NDCG@10 is computed offline by comparing `click_events` positions against returned rankings.

---

## Project structure

```
ecommerce_search/
├── app/
│   ├── main.py                   FastAPI app entry point + router registration
│   ├── config.py                 Pydantic settings (reads from .env)
│   ├── agents/
│   │   ├── __init__.py
│   │   └── search_agents.py      3 CrewAI agents + parse_intent, decide_alpha,
│   │                             build_pinecone_filter, compute_relevancy_score
│   ├── api/
│   │   └── routes.py             /search · /index · /index/bulk · /metrics · /health
│   ├── db/
│   │   └── clients.py            Pinecone + OpenAI singleton clients
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py            SearchRequest · SearchResponse · ProductResult ·
│   │                             ParsedIntent · Product (with to_embedding_text)
│   └── services/
│       ├── __init__.py
│       ├── embedding.py          embed_text · embed_batch · upsert_product · batch upsert
│       ├── ingestion.py          ingest_product · ingest_products_bulk
│       └── search.py             hybrid_search · _query_pinecone · _reciprocal_rank_fusion
│                                 · _sort_results
├── scripts/
│   └── seed_products.py          9 mock products across all 3 categories
├── tests/
│   └── test_search.py            Test stubs for all core functions
├── architecture.html             Interactive architecture reference (open in browser)
├── Dockerfile                    python:3.11-slim image
├── docker-compose.yml            API + Redis + PostgreSQL
├── requirements.txt
├── .env.example
└── README.md
```

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/search` | Run hybrid product search |
| `POST` | `/api/v1/index` | Ingest a single product |
| `POST` | `/api/v1/index/bulk` | Batch ingest products |
| `DELETE` | `/api/v1/index/{product_id}` | Remove a product from the index |
| `GET` | `/api/v1/metrics` | Prometheus metrics scrape endpoint |
| `GET` | `/api/v1/health` | Health check |

Auto-generated OpenAPI docs available at `http://localhost:8000/docs` when running locally.

---

## Setup

### Prerequisites
- Python 3.11+
- A Pinecone account (free tier works for development)
- An OpenAI API key
- Docker (optional, for full stack)

### Local development

```bash
cd ecommerce_search
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in OPENAI_API_KEY, PINECONE_API_KEY, DATABASE_URL in .env
uvicorn app.main:app --reload
```

### Seed products into Pinecone

```bash
python scripts/seed_products.py
```

### Run full stack with Docker

```bash
docker-compose up --build
```

This starts:
- `api` — FastAPI on port 8000
- `redis` — Redis 7 on port 6379
- `postgres` — PostgreSQL 16 on port 5432

---

## Build order

Implement files in this sequence to avoid import errors:

1. `app/db/clients.py` — Pinecone + OpenAI client singletons
2. `app/services/embedding.py` — `embed_text`, `upsert_product`
3. `app/agents/search_agents.py` — `parse_intent_with_llm`, `decide_alpha`, `build_pinecone_filter`, `compute_relevancy_score`
4. `app/services/search.py` — `hybrid_search`, `_reciprocal_rank_fusion`
5. `app/services/ingestion.py` — `ingest_product`, `ingest_products_bulk`
6. `app/api/routes.py` — wire up FastAPI endpoints
7. `scripts/seed_products.py` — seed and verify data in Pinecone
8. `tests/test_search.py` — fill in test stubs

---

## Tech stack

| Concern | Tool | Reason |
|---|---|---|
| Agent orchestration | CrewAI | Native multi-agent roles and task chaining; LangChain under the hood |
| Vector DB | Pinecone | Managed ANN search, namespace-per-category filtering |
| LLM | gpt-4o-mini | JSON output schema, low cost, fast |
| Embeddings | text-embedding-3-small | Best cost/quality ratio for product text |
| Reranking | Cohere Rerank v3 | Cross-encoder precision on top-K candidates |
| Metadata store | PostgreSQL | Product catalog, ratings, click events |
| Cache | Redis | Sub-10ms repeated query responses |
| API layer | FastAPI | Async, OpenAPI docs, Prometheus middleware |
| LLM tracing | LangSmith | Agent trace visibility, latency profiling |
| Metrics | Prometheus + Grafana | 5 project KPI dashboards |
| Deployment | Docker + AWS ECS | Containerised, repeatable, rolling deploys |

> **Why not LangGraph or LangChain directly?** The three-agent pipeline is linear and sequential — exactly what CrewAI handles natively. LangGraph adds complexity only when agents need non-linear loops or conditional branching, which is not required here.

---

## Phase 2 — multimodal upgrade

Planned once text search is stable and KPI baselines are established:

| Feature | Implementation |
|---|---|
| Image search | CLIP embeddings (`openai/clip-vit-large-patch14`) in a separate Pinecone namespace; image query → vector similarity |
| Voice search | OpenAI Whisper STT → text transcript → existing Phase 1 pipeline; no agent changes |
| Multilingual | Swap embedding model for `multilingual-e5-large`; evaluate with BLEU score vs Google Translate baseline |
