# Implementation Plan — E-Commerce Search Engine

## Overview

This document tracks the implementation plan across three phases. Phase 1 is the core text-based search pipeline. Phase 2 adds multimodal input (image, voice). Phase 3 applies agentic design patterns from the [Fourkites AI Excellence training](../Fourkites_AIExcellence/) to improve quality, resilience, and observability.

---

## Phase 1 — Core text-based search (current)

All functions are stubbed with `NotImplementedError`. Implement in this order to avoid import errors.

### Build order

| Step | File | Functions | Status |
|---|---|---|---|
| 1 | `app/db/clients.py` | `get_pinecone_index()`, `get_gemini_client()` | Stub |
| 2 | `app/services/embedding.py` | `embed_text()`, `embed_batch()`, `upsert_product()`, `upsert_products_batch()`, `delete_product()` | Stub |
| 3 | `app/agents/search_agents.py` | `parse_intent_with_llm()`, `decide_alpha()`, `build_pinecone_filter()`, `compute_relevancy_score()` | Stub |
| 4 | `app/agents/search_agents.py` | `build_query_analyst()`, `build_search_strategist()`, `build_results_ranker()` | Stub |
| 5 | `app/services/search.py` | `hybrid_search()`, `_query_pinecone()`, `_reciprocal_rank_fusion()`, `_sort_results()` | Stub |
| 6 | `app/services/ingestion.py` | `ingest_product()`, `ingest_products_bulk()` | Stub |
| 7 | `app/api/routes.py` | All 6 endpoints | Stub |
| 8 | `app/main.py` | Add middleware (Redis cache, request latency, CORS) | Partial |
| 9 | `scripts/seed_products.py` | Seed 9 mock products and verify in Pinecone | Ready |
| 10 | `tests/test_search.py` | Fill in 6 test stubs | Stub |

### Key decisions

- **Embedding model:** all-MiniLM-L6-v2 (384 dims, ~80MB) — free local inference via sentence-transformers
- **LLM:** Gemini 2.5 Flash — JSON output schema, free tier, fast
- **Vector DB:** Pinecone serverless — namespace per category, metadata filtering, dim=384
- **Keyword ranking:** Token overlap simulation (true BM25 requires Pinecone sparse-dense upgrade)
- **RRF damping constant:** k = 60

### Environment variables required

```
GEMINI_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX=ecommerce-search
HF_TOKEN=
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ecommerce
REDIS_URL=redis://localhost:6379
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
```

---

## Phase 2 — Multimodal upgrade

Planned once Phase 1 is stable and KPI baselines are established.

| Feature | Model | Integration point | New dependencies |
|---|---|---|---|
| Image search | CLIP (`openai/clip-vit-large-patch14`, 768 dims) | Separate Pinecone namespace per category | `transformers`, `torch`, `Pillow` |
| Voice search | OpenAI Whisper STT | Transcribe → feed into Phase 1 pipeline | `openai` (already present) |
| Multilingual | `multilingual-e5-large` | Swap embedding model, re-index | `sentence-transformers` |

### Build order

| Step | Task | Depends on |
|---|---|---|
| 1 | Add CLIP embedding service | Phase 1 embedding service |
| 2 | Create image Pinecone namespaces | Phase 1 Pinecone setup |
| 3 | Add `/search/image` API endpoint | CLIP service |
| 4 | Add Whisper transcription service | — |
| 5 | Add `/search/voice` API endpoint | Whisper service + Phase 1 search |
| 6 | Swap to multilingual embeddings | Phase 1 stable |
| 7 | BLEU score evaluation | Phase 1 eval pipeline |

---

## Phase 3 — Agentic design pattern enhancements

Improvements derived from [Agentic Design Patterns](../Fourkites_AIExcellence/Agentic%20Design%20Patterns/) and [Observability](../Fourkites_AIExcellence/Observability/) training.

### Build order

| Step | Enhancement | Pattern | File(s) | Priority | Depends on |
|---|---|---|---|---|---|
| 1 | Parallel semantic + keyword retrieval | Parallelization | `app/services/search.py` | High | Phase 1 step 5 |
| 2 | LangSmith agent tracing | Observability | `app/main.py` | High | Phase 1 step 8 |
| 3 | Reflection loop on Results Ranker | Reflection | `app/agents/evaluator.py` (new), `app/agents/search_agents.py` | High | Phase 1 step 4 |
| 4 | Category-aware routing | Routing | `app/agents/search_agents.py` | Medium | Phase 1 step 3 |
| 5 | Input guardrails | Guardrails | `app/middleware/guardrails.py` (new) | Medium | Phase 1 step 7 |
| 6 | Multi-agent handoff (compound queries) | Multi-Agent | `app/agents/search_agents.py` | Medium | Phase 1 step 3 |
| 7 | RAG evaluation with Ragas | Evaluation | `scripts/evaluate_search.py` (new) | Medium | Phase 1 step 9 |

### Detailed implementation notes

#### 3.1 Parallel retrieval (`asyncio.gather`)

Refactor `hybrid_search()` to run semantic and keyword paths concurrently:

```python
async def hybrid_search(request: SearchRequest) -> SearchResponse:
    intent = await parse_intent_with_llm(request.query, request)
    alpha = decide_alpha(intent)
    filters = build_pinecone_filter(intent)
    query_vector = await embed_text(request.query)

    # Parallel execution — saves ~40% latency
    semantic_results, keyword_results = await asyncio.gather(
        _query_pinecone(query_vector, intent.category, request.top_k, filters),
        _keyword_search(request.query, intent.category)
    )

    merged = _reciprocal_rank_fusion(semantic_results, keyword_results, alpha)
    scored = [compute_relevancy_score(r) for r in merged]
    return _sort_results(scored, request.sort_by)
```

#### 3.2 Reflection loop

```
Results Ranker → Evaluate(avg_score, diversity) → PASS → Return results
                                                 → FAIL → Adjust alpha ±0.15
                                                        → Relax filters
                                                        → Increase top_k by 20
                                                        → Re-run (max 2 retries)
```

Pydantic schema:
```python
class EvaluationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"

class EvaluationResult(BaseModel):
    status: EvaluationStatus
    avg_relevancy: float
    feedback: str
    adjusted_alpha: float | None = None
    adjusted_top_k: int | None = None
```

#### 3.3 Category-aware routing

Enhance `decide_alpha()` to use both specificity AND category:

```python
def decide_alpha(intent: ParsedIntent) -> float:
    category_defaults = {
        "electronics": 0.3,   # spec-heavy, keyword matters
        "shoes": 0.8,         # aesthetic, semantic matters
        "stationery": 0.5,    # balanced
    }
    base = category_defaults.get(intent.category, 0.6)

    # Adjust by specificity
    if intent.specificity == "high":
        return max(base - 0.2, 0.1)
    elif intent.specificity == "low":
        return min(base + 0.15, 0.95)
    return base
```

#### 3.4 Input guardrails

```python
# app/middleware/guardrails.py
BLOCKED_PATTERNS = [
    r"ignore.*instructions",
    r"system.*prompt",
    r"forget.*everything",
]

async def validate_query(query: str) -> tuple[bool, str]:
    if len(query.strip()) < 2:
        return False, "Query too short"
    if len(query) > 500:
        return False, "Query too long"
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            return False, "Query blocked by guardrail"
    return True, ""
```

---

## Cross-reference: Training → Project mapping

| Training Module | Pattern/Technique | Applied in Phase |
|---|---|---|
| `Agentic Design Patterns/Prompt_Chaining.py` | Sequential agent pipeline | Phase 1 (baseline) |
| `Agentic Design Patterns/Reflection.py` | Self-critique + iterative refinement | Phase 3.1 |
| `Agentic Design Patterns/Routing.py` | Category-aware dynamic routing | Phase 3.4 |
| `Agentic Design Patterns/Parallelization.py` | Async concurrent retrieval | Phase 3.1 |
| `Agentic Design Patterns/MultiAgent.py` | Compound query handoff | Phase 3.6 |
| `Agentic Frameworks/CrewAI/` | Multi-agent orchestration | Phase 1 (baseline) |
| `Orchestration Frameworks/LlamaIndex/RAG_Pinecone.ipynb` | Pinecone vector search | Phase 1 (baseline) |
| `Orchestration Frameworks/LlamaIndex/RAG_ChromaDB.ipynb` | HuggingFace embeddings | Phase 3.8 |
| `Orchestration Frameworks/LlamaIndex/RAG_Weaviate.ipynb` | Hybrid search (BM25 + vector) | Phase 1 (RRF approach) |
| `Observability/CrewAI_Langsmith.py` | Agent tracing | Phase 3.2 |
| `Evals_and_Embeddings/` | BLEU, ROUGE, Ragas metrics | Phase 3.7 |
| `Agentic Deployment/` | Guardrails, input validation | Phase 3.5 |
