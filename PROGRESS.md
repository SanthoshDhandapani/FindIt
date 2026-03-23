# FindIt — Project Progress

**Repository:** [SanthoshDhandapani/FindIt](https://github.com/SanthoshDhandapani/FindIt)
**Last updated:** 2026-03-23

---

## Project Overview

**FindIt** is an AI-powered e-commerce product search engine that uses semantic search, hybrid retrieval (RRF), and multi-agent orchestration to deliver relevant product results from natural language queries.

### Tech Stack

| Concern | Tool |
|---|---|
| LLM | Gemini 2.5 Flash (free tier, JSON schema output) |
| Embeddings | all-MiniLM-L6-v2 (384 dims, ~80MB, local via sentence-transformers) |
| Agent Orchestration | CrewAI v1.11.0 (3 agents, sequential pipeline) |
| Vector DB | Pinecone serverless (384 dims, cosine, namespace-per-category) |
| API | FastAPI with Redis cache + latency tracking middleware |
| Database | PostgreSQL 17 (product catalog, via Docker on port 5433) |
| Cache | Redis 7 (query caching, 5 min TTL) |
| Frontend | React + Vite (port 3000, proxied to backend) |

---

## Track Completion Status

| Track | Issues | Closed | Status |
|---|---|---|---|
| **A — Foundation** | #1, #2, #3 | 3/3 | **Complete** |
| **B — Data Pipeline** | #4, #5, #6 | 3/3 | **Complete** |
| **C — Search Intelligence** | #7, #8, #9, #10 | 4/4 | **Complete** |
| **D — API Layer** | #11, #12 | 2/2 | **Complete** |
| **E — Search UI** | #13, #14, #15, #16, #17 | 1/5 | In Progress |
| **F — Agentic Enhancements** | #18-#23 | 0/6 | Not Started |

**Overall: 13/23 issues closed**

---

## Commit History

| Commit | Description | Issues |
|---|---|---|
| `c0abb92` | Initial commit: ecommerce search application skeleton | — |
| `22add82` | Add Phase 3 agentic design pattern enhancements skeleton | — |
| `3909f39` | Switch from OpenAI to Gemini LLM + all-MiniLM-L6-v2 embeddings | #1 |
| `39bab84` | Implement Pinecone and Gemini client singletons | #3 |
| `64a57fa` | Implement embedding service with all-MiniLM-L6-v2 | #4 |
| `d7c7fd2` | Implement ingestion pipeline and seed 210 products | #5, #6 |
| `49f494f` | Bootstrap React frontend with Vite, API client, and search UI | #14 |
| `b288c30` | Fix: resolve python-dotenv version conflict and comment out crewai | — |
| `debc33e` | Implement LLM intent parsing and search strategy helpers | #7, #8 |
| `a7befa8` | Implement hybrid search engine with RRF | #10 |
| `dbd06b2` | Fix UI | — |
| `b4387c3` | Implement CrewAI agent definitions and search crew | #9 |
| `18789a0` | Wire up all FastAPI routes to implemented services | #11 |
| `378158d` | Add CORS, latency tracking, and Redis cache middleware | #12 |
| `edbf059` | Connect frontend to live backend API | — |
| `9d9ff23` | Update requirements.txt — unpin versions, add crewai | — |
| `86d2a52` | Fix pinecone package — use pinecone-client>=4.0,<6 | — |
| `d2794f8` | Fix frontend: increase proxy timeout, skip empty initial query | — |

---

## What Was Built

### Track A — Foundation

**Issue #1: Environment & Infrastructure Setup**
- Created `.env` with keys: `GEMINI_API_KEY`, `PINECONE_API_KEY`, `HF_TOKEN`, `DATABASE_URL`, `REDIS_URL`
- Docker Compose: PostgreSQL 17 (port 5433) + Redis 7 (port 6379) via Rancher Desktop
- Pinecone index `ecommerce-search` created (384 dims, cosine, serverless, us-east-1)
- Created `scripts/validate_setup.py` — validates all 6 components (10/10 pass)
- **Key decision:** Switched from OpenAI to Gemini (LLM) + all-MiniLM-L6-v2 (embeddings) for zero API cost

**Issue #2: Product Data Collection**
- 210 products across 3 categories: Electronics (70), Shoes (70), Clothes (70)
- `files/products.json` — 81 products with image URLs (50 electronics, 31 clothes)
- `files/combined_products.json` — 210 products without images (full set)
- Note: Shoes don't have image URLs yet (from old data file)

**Issue #3: Database Client Singletons**
- `get_pinecone_index()` — singleton Pinecone index connection
- `get_gemini_client()` — singleton Gemini API client
- Both use module-level caching (`_pinecone_index`, `_gemini_client`)

### Track B — Data Pipeline

**Issue #4: Embedding Service**
- `embed_text(text) → list[float]` — single text → 384-dim vector
- `embed_batch(texts) → list[list[float]]` — batch encode (more efficient)
- Lazy singleton model loading via `_get_model()`
- Model: `sentence-transformers/all-MiniLM-L6-v2`

**Issue #5: Ingestion Pipeline**
- `upsert_product(product)` — embed + upsert single product to Pinecone
- `upsert_products_batch(products)` — batch embed + upsert grouped by category, 100 per batch
- `delete_product(product_id, category)` — remove vector by ID and namespace
- `ingest_product(product) → dict` — wrapper with latency tracking
- `ingest_products_bulk(products) → dict` — bulk wrapper with summary stats
- Updated `Product` schema: `stationery` → `clothes`, optional `rating`/`review_count`

**Issue #6: Seed Products**
- Seeded 210 products into Pinecone (70 per namespace: electronics, shoes, clothes)
- Seed script: `scripts/seed_products.py` loads from `files/products.json`

### Track C — Search Intelligence

**Issue #7: LLM Intent Parsing**
- `parse_intent_with_llm(query, request) → ParsedIntent`
- Calls Gemini 2.5 Flash with JSON output schema
- Extracts: category, brand, color, price range, sort, keywords, specificity
- Explicit `SearchRequest` filters override LLM inference
- Graceful fallback on Gemini failure (empty intent with defaults)

**Issue #8: Search Strategy Helpers**
- `decide_alpha(intent) → float` — specificity-based blend weight
  - high → 0.2 (keyword-heavy), medium → 0.6, low → 0.85 (semantic-heavy)
- `build_pinecone_filter(intent) → dict` — constructs `$eq`, `$gte`, `$lte` filters
- `compute_relevancy_score(similarity, rating, review_count) → float`
  - Formula: `(1 - 0.2) * similarity + 0.2 * (rating/5) + min(review_count/1000, 1.0) * 0.05`

**Issue #9: CrewAI Agent Definitions**
- `build_query_analyst()` — Agent: parses queries into structured intent
- `build_search_strategist()` — Agent: decides alpha + builds filters
- `build_results_ranker()` — Agent: re-scores by similarity + rating + reviews
- `build_search_crew()` — Crew: sequential pipeline (Analyst → Strategist → Ranker)
- Uses `gemini/gemini-2.5-flash` via CrewAI's LiteLLM integration

**Issue #10: Hybrid Search Engine with RRF**
- `hybrid_search(request) → SearchResponse` — full 9-step pipeline
- `_query_pinecone(vector, namespace, top_k, filters)` — Pinecone vector query
- `_keyword_search(query, namespace)` — token overlap scoring on name + brand + color
- `_reciprocal_rank_fusion(semantic, keyword, alpha, k=60)` — RRF merge with dedup
- `_sort_results(results, sort_by)` — sort by relevancy/rating/price
- `async_hybrid_search()` — async version with `asyncio.gather` for parallel retrieval

### Track D — API Layer

**Issue #11: FastAPI Routes**
- `POST /api/v1/search` — calls `hybrid_search()`, returns `SearchResponse`
- `POST /api/v1/index` — single product ingestion
- `POST /api/v1/index/bulk` — batch ingestion
- `DELETE /api/v1/index/{product_id}` — delete from Pinecone
- `GET /api/v1/health` — checks Pinecone (210 vectors) + Redis connectivity

**Issue #12: Middleware**
- **CORS**: allows localhost:3000 (React) + localhost:5173 (Vite)
- **LatencyMiddleware**: logs timing, adds `X-Latency-Ms` response header
- **RedisCacheMiddleware**: caches `POST /search` responses
  - Cache key: MD5 hash of request body
  - TTL: 5 min default, 30s for `sort_by=rating`
  - `X-Cache: HIT/MISS` header
- **LangSmith tracing**: auto-enabled when `LANGCHAIN_TRACING_V2=true`

### Track E — Search UI (Partial)

**Issue #14: React App Setup**
- React + Vite on port 3000, proxy `/api` → `http://localhost:8000`
- Components: SearchBar, ProductCard, ProductGrid, SortBar, Filters
- API client: `searchProducts()` with `USE_MOCK=false` (connected to real backend)
- Types aligned with backend `SearchResponse`/`ProductResult` schemas

---

## Known Issues

1. **Shoes have no image URLs** — the 70 shoe products were seeded from `combined_products.json` (no images). `products.json` has images but no shoes. Need to add shoes with images and re-seed.
2. **Search latency is 5-13 seconds** — primarily due to Gemini API call for intent parsing + two Pinecone queries (semantic + keyword). Phase 3 async parallel retrieval (#18) will help.
3. **Gemini free tier rate limits** — 20 requests/day on gemini-2.5-flash (old key), new key has higher limits.

---

## How to Run

```bash
# 1. Start Docker services
DOCKER_HOST=unix://$HOME/.rd/docker.sock docker-compose up -d redis postgres

# 2. Start backend
cd /Users/santhosh.d/Documents/dev/AI_Training/ecommerce_search
source /Users/santhosh.d/Documents/dev/AI_Training/.venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --reload

# 3. Start frontend (separate terminal)
cd frontend
pnpm dev

# 4. Open http://localhost:3000
# 5. API docs at http://localhost:8000/docs
```

### Validation
```bash
PYTHONPATH=. python scripts/validate_setup.py
# Should show 10/10 passed
```

### Re-seed products
```bash
PYTHONPATH=. python scripts/seed_products.py
```

---

## Remaining Work

### Track E — Search UI (#13, #15, #16, #17)
- UI design wireframe
- Search page with filter sidebar (category, brand, color, price range)
- Results grid polish and product card refinements
- Loading skeletons, empty state, error handling

### Track F — Agentic Enhancements (#18-#23)
- #18: Async parallel retrieval (`asyncio.gather` for semantic + keyword)
- #19: Reflection loop (retry with adjusted alpha if low relevancy)
- #20: Category-aware routing (per-category alpha base values)
- #21: Input guardrails (prompt injection guard, query sanitization)
- #22: Multi-agent handoff (compound queries → split + merge)
- #23: HuggingFace embedding fallback (cost optimization)
