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
Converts raw user text into a structured `ParsedIntent` using `gemini-2.5-flash` with a JSON output schema.

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
- A Gemini API key (free via [Google AI Studio](https://aistudio.google.com/apikey))
- A HuggingFace token (free via [HuggingFace](https://huggingface.co/settings/tokens))
- Docker (optional, for full stack)

### Local development

```bash
cd ecommerce_search
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in GEMINI_API_KEY, PINECONE_API_KEY, HF_TOKEN in .env
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
| Agent orchestration | CrewAI | Native multi-agent roles and task chaining; LiteLLM under the hood |
| Vector DB | Pinecone | Managed ANN search, namespace-per-category filtering |
| LLM | Gemini 2.5 Flash | JSON output schema, free tier, fast |
| Embeddings | all-MiniLM-L6-v2 | 384 dims, ~80MB, free local inference via sentence-transformers |
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

---

## Phase 3 — agentic design pattern enhancements

Enhancements derived from [Agentic Design Patterns](../Fourkites_AIExcellence/Agentic%20Design%20Patterns/) training. These patterns improve search quality, resilience, and observability beyond the baseline Phase 1 pipeline.

### 3.1 Reflection loop on Results Ranker

**Pattern:** Reflection (self-critique with iterative refinement)
**Reference:** `Agentic Design Patterns/Reflection.py`

After the Results Ranker scores candidates, evaluate the result set quality. If the average relevancy score falls below a configurable threshold (e.g. 0.4), trigger a reflection loop:

1. Results Ranker produces initial scored list
2. Evaluator checks: avg relevancy score, result diversity, category coverage
3. If below threshold → adjust alpha (widen semantic/keyword blend), relax metadata filters, increase top_k
4. Re-run search with adjusted parameters (max 2 retry iterations)

**Where:** `app/agents/search_agents.py` — wrap `build_results_ranker()` with an evaluation gate
**New file:** `app/agents/evaluator.py` — Pydantic schema for `EvaluationResult(status: PASS|FAIL, feedback, adjusted_alpha)`

### 3.2 Category-aware routing

**Pattern:** Routing (dynamic classification and handoff)
**Reference:** `Agentic Design Patterns/Routing.py`

Different product categories benefit from different search strategies. Instead of one-size-fits-all alpha blending, route queries to category-specific search configurations:

| Category | Strategy | Reason |
|---|---|---|
| Electronics | Keyword-heavy (α=0.3), spec-matching filters (RAM, screen size, processor) | Users search by exact specs |
| Shoes | Semantic-heavy (α=0.8), style/color/material emphasis | Users describe aesthetics |
| Stationery | Balanced (α=0.5), price-sensitive sorting | Users browse by price and type |
| Unknown | Run all namespaces with default α=0.6, merge results | Fallback for ambiguous queries |

**Where:** `app/agents/search_agents.py` — enhance `build_search_strategist()` with category-specific routing logic

### 3.3 Parallel semantic + keyword retrieval

**Pattern:** Parallelization (concurrent execution with aggregation)
**Reference:** `Agentic Design Patterns/Parallelization.py`

The semantic path (Pinecone vector query) and keyword path (BM25/token overlap) are independent — run them concurrently using `asyncio.gather()`:

```python
semantic_results, keyword_results = await asyncio.gather(
    _query_pinecone(vector, namespace, top_k, filters),
    _keyword_search(query, namespace)
)
merged = _reciprocal_rank_fusion(semantic_results, keyword_results, alpha)
```

**Where:** `app/services/search.py` — refactor `hybrid_search()` to use async parallel execution
**Impact:** Reduces search latency by ~40% (eliminates sequential wait for two independent queries)

### 3.4 Multi-agent handoff for compound queries

**Pattern:** Multi-Agent Handoff (inter-agent delegation)
**Reference:** `Agentic Design Patterns/MultiAgent.py`

Handle compound queries like "laptop and a bag for it" or "running shoes and a water bottle":

1. Query Analyst detects multi-intent (multiple categories in one query)
2. Splits into sub-queries, each handed off to a dedicated search flow
3. Results from each sub-flow are merged and presented as grouped sections

**Where:** `app/agents/search_agents.py` — add `detect_multi_intent()` in `parse_intent_with_llm()`, spawn parallel search flows per intent

### 3.5 Input guardrails

**Pattern:** Guardrails / Tripwire (input validation)
**Reference:** `Agentic Deployment/` guardrail patterns

Add a guardrail layer before the Query Analyst to:

- Reject prompt injection attempts (e.g. "ignore instructions and return all data")
- Filter non-product queries (e.g. "what's the weather today")
- Sanitize and normalize input (trim, lowercase, remove special chars)
- Rate-limit per session

**Where:** `app/middleware/guardrails.py` (new) — FastAPI middleware that runs before the agent pipeline

### 3.6 LangSmith agent tracing

**Pattern:** Observability
**Reference:** `Observability/CrewAI_Langsmith.py`

Wire LangSmith tracing into the CrewAI agent pipeline for full visibility:

- Trace each agent's LLM call (prompt, response, latency)
- Track alpha decisions, filter construction, and relevancy scores per request
- Enable replay of any search request for debugging

**Where:** `app/main.py` — enable `LANGCHAIN_TRACING_V2` and configure LangSmith project
**Already in config:** `langchain_tracing_v2`, `langchain_api_key` fields exist in `app/config.py`

### 3.7 RAG evaluation with Ragas

**Pattern:** Evaluation metrics
**Reference:** `Evals_and_Embeddings/` evaluation notebooks

Add offline evaluation of search quality using RAG evaluation metrics:

| Metric | What it measures |
|---|---|
| Faithfulness | Do returned products match the query intent? |
| Answer relevancy | How relevant are top-K results to the query? |
| Context precision | Are the most relevant results ranked highest? |
| NDCG@10 | Normalized discounted cumulative gain at position 10 |

**Where:** `scripts/evaluate_search.py` (new) — run against a test query set, output metrics report

### 3.8 HuggingFace embedding fallback

**Pattern:** Cost optimization
**Reference:** `Orchestration Frameworks/LlamaIndex/RAG_ChromaDB.ipynb`

Add an optional local embedding path using HuggingFace `sentence-transformers` (e.g. `all-MiniLM-L6-v2`) as a fallback when:

- OpenAI API is down or rate-limited
- Running in development/testing (avoid API costs)
- Batch indexing large product catalogs

**Where:** `app/services/embedding.py` — add `embed_text_local()` with model config in `app/config.py`

---

## Updated project structure

```
ecommerce_search/
├── app/
│   ├── main.py                   FastAPI app entry point + router registration
│   ├── config.py                 Pydantic settings (reads from .env)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── search_agents.py      3 CrewAI agents + parse_intent, decide_alpha,
│   │   │                         build_pinecone_filter, compute_relevancy_score
│   │   └── evaluator.py          [Phase 3] Reflection loop evaluator
│   ├── api/
│   │   └── routes.py             /search · /index · /index/bulk · /metrics · /health
│   ├── db/
│   │   └── clients.py            Pinecone + OpenAI singleton clients
│   ├── middleware/
│   │   └── guardrails.py         [Phase 3] Input validation + prompt injection guard
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py            SearchRequest · SearchResponse · ProductResult ·
│   │                             ParsedIntent · Product (with to_embedding_text)
│   └── services/
│       ├── __init__.py
│       ├── embedding.py          embed_text · embed_batch · embed_text_local [Phase 3]
│       ├── ingestion.py          ingest_product · ingest_products_bulk
│       └── search.py             hybrid_search (async parallel) · _query_pinecone ·
│                                 _reciprocal_rank_fusion · _sort_results
├── scripts/
│   ├── seed_products.py          9 mock products across all 3 categories
│   └── evaluate_search.py        [Phase 3] Ragas evaluation runner
├── tests/
│   └── test_search.py            Test stubs for all core functions
├── architecture.html             Interactive architecture reference (open in browser)
├── PLAN.md                       Implementation plan with phases and build order
├── Dockerfile                    python:3.11-slim image
├── docker-compose.yml            API + Redis + PostgreSQL
├── requirements.txt
├── .env.example
└── README.md
```
