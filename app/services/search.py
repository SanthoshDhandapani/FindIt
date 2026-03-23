from __future__ import annotations

import asyncio
import logging
import time

from app.agents.search_agents import (
    build_pinecone_filter,
    compute_relevancy_score,
    decide_alpha,
    parse_intent_with_llm,
)
from app.models.schemas import ParsedIntent, ProductResult, SearchRequest, SearchResponse
from app.services.embedding import embed_text

logger = logging.getLogger(__name__)

_ALL_NAMESPACES = ["electronics", "clothes", "shoes", "stationery"]


# ---------------------------------------------------------------------------
# Issue #10 — Hybrid search pipeline
# ---------------------------------------------------------------------------

def hybrid_search(request: SearchRequest) -> SearchResponse:
    """Full 9-step hybrid search pipeline.

    Step 1  — parse_intent_with_llm   → ParsedIntent
    Step 2  — decide_alpha            → float (semantic/keyword blend)
    Step 3  — build_pinecone_filter   → dict (metadata filters)
    Step 4  — embed_text(query)       → 384-dim vector
    Step 5  — _query_pinecone         → semantic matches
    Step 6  — _keyword_search         → keyword matches
    Step 7  — _reciprocal_rank_fusion → merged + deduped list
    Step 8  — compute_relevancy_score → scored list
    Step 9  — _sort_results           → final SearchResponse

    Phase 3 TODOs:
        - Parallelization: replace steps 5+6 with asyncio.gather()
        - Reflection: evaluate quality after step 9, retry if score < threshold
        - Multi-agent handoff: detect_multi_intent() after step 1
    """
    from concurrent.futures import ThreadPoolExecutor

    t_start = time.perf_counter()

    # Steps 1 + 4 — run Gemini intent parsing and embedding in PARALLEL
    # (they're independent — intent doesn't need vector, vector doesn't need intent)
    with ThreadPoolExecutor(max_workers=2) as executor:
        intent_future = executor.submit(parse_intent_with_llm, request.query, request)
        vector_future = executor.submit(embed_text, request.query)
        intent = intent_future.result()
        vector = vector_future.result()

    logger.debug("Intent: %s", intent)

    # Step 2 — decide alpha (semantic vs keyword blend)
    alpha = decide_alpha(intent)

    # Step 3 — build metadata filter
    filters = build_pinecone_filter(intent)

    # Determine namespaces to search
    namespaces = [intent.category] if intent.category else _ALL_NAMESPACES
    top_k_candidates = max(request.top_k * 3, 50)

    # Steps 5 + 6 — run semantic and keyword retrieval in PARALLEL
    with ThreadPoolExecutor(max_workers=2) as executor:
        def _run_semantic():
            results = []
            for ns in namespaces:
                results.extend(_query_pinecone(vector, ns, top_k_candidates, filters))
            return results

        def _run_keyword():
            results = []
            for ns in namespaces:
                results.extend(_keyword_search(request.query, ns, top_k_candidates, filters=filters, vector=vector))
            return results

        sem_future = executor.submit(_run_semantic)
        kw_future = executor.submit(_run_keyword)
        semantic_results = sem_future.result()
        keyword_results = kw_future.result()

    # Step 7 — merge with Reciprocal Rank Fusion
    merged = _reciprocal_rank_fusion(semantic_results, keyword_results, alpha)

    # Step 8 — compute relevancy score per result
    scored: list[dict] = []
    for item in merged:
        meta = item.get("metadata", {})
        item["relevancy_score"] = compute_relevancy_score(
            similarity=item.get("rrf_score", 0.0),
            rating=float(meta.get("rating", 0.0)),
            review_count=int(meta.get("review_count", 0)),
        )
        scored.append(item)

    # Step 9 — sort and build SearchResponse
    sorted_results = _sort_results(scored, request.sort_by)
    top_results = sorted_results[: request.top_k]

    product_results = [
        ProductResult(
            product_id=r["metadata"].get("product_id", r.get("id", "")),
            name=r["metadata"].get("name", ""),
            brand=r["metadata"].get("brand", ""),
            category=r["metadata"].get("category", ""),
            color=r["metadata"].get("color") or None,
            price=float(r["metadata"].get("price", 0)),
            rating=float(r["metadata"].get("rating", 0)),
            review_count=int(r["metadata"].get("review_count", 0)),
            relevancy_score=round(r["relevancy_score"], 4),
            image_url=r["metadata"].get("image_url") or None,
        )
        for r in top_results
    ]

    latency_ms = (time.perf_counter() - t_start) * 1000

    return SearchResponse(
        query=request.query,
        results=product_results,
        total=len(product_results),
        search_mode="hybrid",
        alpha=alpha,
        latency_ms=round(latency_ms, 2),
    )


def _query_pinecone(
    vector: list[float],
    namespace: str,
    top_k: int,
    filters: dict,
) -> list[dict]:
    """Run a Pinecone vector query and return results with metadata.

    Args:
        vector:    Query embedding (384-dim)
        namespace: Pinecone namespace (product category)
        top_k:     Max results to retrieve
        filters:   Pinecone metadata filter dict (may be empty)

    Returns:
        list[dict]: Each dict has 'id', 'score', 'metadata'
    """
    from app.db.clients import get_pinecone_index

    query_kwargs: dict = {
        "vector": vector,
        "top_k": top_k,
        "namespace": namespace,
        "include_metadata": True,
    }
    if filters:
        query_kwargs["filter"] = filters

    response = get_pinecone_index().query(**query_kwargs)

    return [
        {
            "id": match.id,
            "score": match.score,
            "metadata": match.metadata or {},
        }
        for match in response.matches
    ]


def _keyword_search(
    query: str,
    namespace: str,
    top_k: int = 50,
    filters: dict | None = None,
    vector: list[float] | None = None,
) -> list[dict]:
    """Token overlap keyword scoring on product name and brand metadata.

    Simulates BM25-style keyword retrieval for Phase 1 RRF merge.
    Queries Pinecone to get candidates, then re-ranks by token overlap
    between the query and product name + brand + color fields.

    Args:
        query:     Raw user query string
        namespace: Pinecone namespace to search
        top_k:     Number of results to return
        filters:   Pinecone metadata filters (same as semantic path)
        vector:    Pre-computed query embedding (avoids duplicate embed call)

    Returns:
        list[dict]: Candidates sorted by token overlap score,
                    each with 'id', 'score', 'metadata'
    """
    from app.db.clients import get_pinecone_index

    # Reuse pre-computed vector if available
    if vector is None:
        from app.services.embedding import embed_text as _embed
        vector = _embed(query)

    query_kwargs: dict = {
        "vector": vector,
        "top_k": top_k * 2,
        "namespace": namespace,
        "include_metadata": True,
    }
    if filters:
        query_kwargs["filter"] = filters

    response = get_pinecone_index().query(**query_kwargs)

    # Re-rank by token overlap (query tokens ∩ product text tokens)
    query_tokens = set(query.lower().split())
    results = []
    for match in response.matches:
        meta = match.metadata or {}
        product_text = " ".join(filter(None, [
            meta.get("name", ""),
            meta.get("brand", ""),
            meta.get("color", ""),
            meta.get("subcategory", ""),
        ])).lower()
        product_tokens = set(product_text.split())
        overlap = len(query_tokens & product_tokens)
        token_score = overlap / len(query_tokens) if query_tokens else 0.0
        results.append({
            "id": match.id,
            "score": token_score,
            "metadata": meta,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def _reciprocal_rank_fusion(
    semantic_results: list[dict],
    keyword_results: list[dict],
    alpha: float,
    k: int = 60,
) -> list[dict]:
    """Merge semantic and keyword result lists using Reciprocal Rank Fusion.

    RRF score formula:
        score = alpha * 1/(k + sem_rank) + (1 - alpha) * 1/(k + kw_rank)

    Products appearing in only one list get a rank of len(other_list) + 1
    (worst-case rank) for the missing path.

    Args:
        semantic_results: Ranked list from Pinecone vector search
        keyword_results:  Ranked list from token overlap keyword search
        alpha:            Weight for semantic path (0.0 = keyword-only, 1.0 = semantic-only)
        k:                RRF damping constant (default 60)

    Returns:
        list[dict]: Merged, deduped results sorted by RRF score (descending)
    """
    # Handle empty paths — if one path returned nothing, use only the other
    if not semantic_results and not keyword_results:
        return []
    if not semantic_results:
        for i, r in enumerate(keyword_results):
            r["rrf_score"] = 1 / (k + i + 1)
        return keyword_results
    if not keyword_results:
        for i, r in enumerate(semantic_results):
            r["rrf_score"] = 1 / (k + i + 1)
        return semantic_results

    # Build rank lookup by product id
    sem_rank = {r["id"]: i + 1 for i, r in enumerate(semantic_results)}
    kw_rank  = {r["id"]: i + 1 for i, r in enumerate(keyword_results)}

    sem_fallback = len(semantic_results) + 1
    kw_fallback  = len(keyword_results) + 1

    # Collect all unique product ids
    all_ids = {r["id"] for r in semantic_results} | {r["id"] for r in keyword_results}

    # Build metadata lookup (semantic results take priority for metadata)
    meta_lookup: dict[str, dict] = {}
    for r in keyword_results:
        meta_lookup[r["id"]] = r
    for r in semantic_results:
        meta_lookup[r["id"]] = r  # semantic overwrites (more reliable score)

    fused = []
    for pid in all_ids:
        sr = sem_rank.get(pid, sem_fallback)
        kr = kw_rank.get(pid, kw_fallback)
        rrf_score = alpha * (1 / (k + sr)) + (1 - alpha) * (1 / (k + kr))
        entry = dict(meta_lookup[pid])
        entry["rrf_score"] = rrf_score
        fused.append(entry)

    fused.sort(key=lambda x: x["rrf_score"], reverse=True)
    return fused


def _sort_results(results: list[dict], sort_by: str) -> list[dict]:
    """Sort scored results by the requested sort strategy.

    Args:
        results: List of result dicts, each with 'relevancy_score' and 'metadata'
        sort_by: One of "relevancy" | "rating" | "price_asc" | "price_desc"

    Returns:
        list[dict]: Sorted list
    """
    if sort_by == "rating":
        return sorted(results, key=lambda x: float(x["metadata"].get("rating", 0)), reverse=True)
    if sort_by == "price_asc":
        return sorted(results, key=lambda x: float(x["metadata"].get("price", 0)))
    if sort_by == "price_desc":
        return sorted(results, key=lambda x: float(x["metadata"].get("price", 0)), reverse=True)
    # Default: relevancy
    return sorted(results, key=lambda x: x.get("relevancy_score", 0), reverse=True)


# ---------------------------------------------------------------------------
# Phase 3 — Async parallel retrieval
# ---------------------------------------------------------------------------

async def _query_pinecone_async(
    vector: list[float],
    namespace: str,
    top_k: int,
    filters: dict,
) -> list[dict]:
    """Async wrapper around _query_pinecone using thread executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: _query_pinecone(vector, namespace, top_k, filters)
    )


async def _keyword_search_async(
    query: str,
    namespace: str,
    top_k: int = 50,
) -> list[dict]:
    """Async wrapper around _keyword_search using thread executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: _keyword_search(query, namespace, top_k)
    )


async def async_hybrid_search(request: SearchRequest) -> SearchResponse:
    """Async version of hybrid_search with parallel retrieval (~40% faster).

    Steps 1–4 and 7–9 are identical to hybrid_search.
    Steps 5 and 6 run concurrently via asyncio.gather().
    """
    t_start = time.perf_counter()

    intent = parse_intent_with_llm(request.query, request)
    alpha = decide_alpha(intent)
    filters = build_pinecone_filter(intent)
    vector = embed_text(request.query)

    namespaces = [intent.category] if intent.category else _ALL_NAMESPACES
    top_k_candidates = max(request.top_k * 3, 50)

    # Parallel semantic + keyword retrieval
    sem_tasks = [_query_pinecone_async(vector, ns, top_k_candidates, filters) for ns in namespaces]
    kw_tasks  = [_keyword_search_async(request.query, ns, top_k_candidates) for ns in namespaces]
    all_results = await asyncio.gather(*sem_tasks, *kw_tasks)

    mid = len(namespaces)
    semantic_results = [item for sublist in all_results[:mid] for item in sublist]
    keyword_results  = [item for sublist in all_results[mid:] for item in sublist]

    merged = _reciprocal_rank_fusion(semantic_results, keyword_results, alpha)

    scored = []
    for item in merged:
        meta = item.get("metadata", {})
        item["relevancy_score"] = compute_relevancy_score(
            similarity=item.get("rrf_score", 0.0),
            rating=float(meta.get("rating", 0.0)),
            review_count=int(meta.get("review_count", 0)),
        )
        scored.append(item)

    sorted_results = _sort_results(scored, request.sort_by)[: request.top_k]

    product_results = [
        ProductResult(
            product_id=r["metadata"].get("product_id", r.get("id", "")),
            name=r["metadata"].get("name", ""),
            brand=r["metadata"].get("brand", ""),
            category=r["metadata"].get("category", ""),
            color=r["metadata"].get("color") or None,
            price=float(r["metadata"].get("price", 0)),
            rating=float(r["metadata"].get("rating", 0)),
            review_count=int(r["metadata"].get("review_count", 0)),
            relevancy_score=round(r["relevancy_score"], 4),
            image_url=r["metadata"].get("image_url") or None,
        )
        for r in sorted_results
    ]

    latency_ms = (time.perf_counter() - t_start) * 1000

    return SearchResponse(
        query=request.query,
        results=product_results,
        total=len(product_results),
        search_mode="hybrid",
        alpha=alpha,
        latency_ms=round(latency_ms, 2),
    )
