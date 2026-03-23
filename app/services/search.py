from app.models.schemas import SearchRequest, SearchResponse


def hybrid_search(request: SearchRequest) -> SearchResponse:
    # TODO: Implement full search pipeline
    # Step 1 — parse_intent_with_llm(request)       → ParsedIntent
    # Step 2 — decide_alpha(intent)                  → float
    # Step 3 — build_pinecone_filter(intent)         → dict
    # Step 4 — embed_text(request.query)             → vector
    # Step 5 — _query_pinecone(vector, ns, k, filter)→ semantic matches
    # Step 6 — keyword ranking (BM25 / overlap)      → keyword matches
    # Step 7 — _reciprocal_rank_fusion(sem, kw, α)   → merged list
    # Step 8 — compute_relevancy_score per result    → final ranked list
    # Step 9 — _sort_results(results, sort_by)       → SearchResponse
    raise NotImplementedError


def _query_pinecone(
    vector: list[float],
    namespace: str,
    top_k: int,
    filters: dict,
) -> list[dict]:
    # TODO: Run Pinecone vector query with metadata filters
    raise NotImplementedError


def _reciprocal_rank_fusion(
    semantic_results: list[dict],
    keyword_results: list[dict],
    alpha: float,
    k: int = 60,
) -> list[dict]:
    # TODO: Merge semantic + keyword rankings using RRF
    # RRF score = alpha * 1/(k + sem_rank) + (1-alpha) * 1/(k + kw_rank)
    raise NotImplementedError


def _sort_results(results: list, sort_by: str) -> list:
    # TODO: Sort ProductResult list by relevancy | rating | price_asc | price_desc
    raise NotImplementedError
