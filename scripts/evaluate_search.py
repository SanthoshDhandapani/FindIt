"""
Phase 3 — RAG evaluation script.

Pattern: Evaluation metrics
Reference: Evals_and_Embeddings/ evaluation notebooks

Runs a set of test queries against the search API and computes quality metrics:
- Faithfulness: Do returned products match query intent?
- Answer relevancy: How relevant are top-K results?
- Context precision: Are the best results ranked highest?
- NDCG@10: Normalized Discounted Cumulative Gain at position 10

Usage: python scripts/evaluate_search.py
"""

import math
from app.models.schemas import SearchRequest, SearchResponse


# Test query set with expected results for evaluation
TEST_QUERIES = [
    {
        "query": "red Nike shoes under 200",
        "expected_category": "shoes",
        "expected_brand": "Nike",
        "expected_color": "red",
        "expected_product_ids": ["shoe-001"],
    },
    {
        "query": "laptop with 32GB RAM",
        "expected_category": "electronics",
        "expected_brand": None,
        "expected_product_ids": ["elec-002"],
    },
    {
        "query": "dotted notebook for journaling",
        "expected_category": "stationery",
        "expected_brand": None,
        "expected_product_ids": ["stat-001"],
    },
    {
        "query": "comfortable running shoes",
        "expected_category": "shoes",
        "expected_brand": None,
        "expected_product_ids": ["shoe-001", "shoe-002"],
    },
    {
        "query": "insulated water bottle",
        "expected_category": "stationery",
        "expected_brand": None,
        "expected_product_ids": ["stat-002"],
    },
]


def compute_ndcg_at_k(
    ranked_ids: list[str],
    relevant_ids: list[str],
    k: int = 10,
) -> float:
    """Compute Normalized Discounted Cumulative Gain at position k.

    Args:
        ranked_ids: Product IDs in the order returned by search
        relevant_ids: Product IDs considered relevant (ground truth)
        k: Cutoff position

    Returns:
        NDCG@k score between 0.0 and 1.0
    """
    # TODO: Compute DCG@k = sum of (1 / log2(i + 2)) for relevant items at position i
    # TODO: Compute IDCG@k = best possible DCG with all relevant items at top
    # TODO: Return DCG / IDCG (handle division by zero)
    raise NotImplementedError


def compute_precision_at_k(
    ranked_ids: list[str],
    relevant_ids: list[str],
    k: int = 10,
) -> float:
    """Compute precision at position k.

    Returns fraction of top-k results that are relevant.
    """
    # TODO: Count how many of ranked_ids[:k] appear in relevant_ids
    # TODO: Return count / k
    raise NotImplementedError


def compute_avg_relevancy(response: SearchResponse) -> float:
    """Compute average relevancy score across all results."""
    # TODO: Return mean of result.relevancy_score for all results
    # TODO: Return 0.0 if no results
    raise NotImplementedError


def evaluate_single_query(query_spec: dict) -> dict:
    """Run a single test query and compute metrics.

    Args:
        query_spec: Dict with query, expected_category, expected_brand,
                    expected_product_ids

    Returns:
        Dict with query, ndcg_10, precision_10, avg_relevancy, category_match
    """
    # TODO: Build SearchRequest from query_spec
    # TODO: Call hybrid_search(request)
    # TODO: Extract ranked product IDs from response
    # TODO: Compute NDCG@10, precision@10, avg_relevancy
    # TODO: Check if response category matches expected_category
    # TODO: Return metrics dict
    raise NotImplementedError


def run_evaluation() -> dict:
    """Run full evaluation across all test queries.

    Returns summary metrics dict:
    {
        "total_queries": int,
        "avg_ndcg_10": float,
        "avg_precision_10": float,
        "avg_relevancy": float,
        "category_accuracy": float,
        "per_query": list[dict],
    }
    """
    # TODO: Loop through TEST_QUERIES, call evaluate_single_query for each
    # TODO: Aggregate metrics across all queries
    # TODO: Print formatted report
    # TODO: Return summary dict
    raise NotImplementedError


if __name__ == "__main__":
    print("Running search evaluation...")
    print(f"Test queries: {len(TEST_QUERIES)}")
    print("-" * 60)
    results = run_evaluation()
    print("-" * 60)
    print(f"Average NDCG@10:     {results['avg_ndcg_10']:.3f}")
    print(f"Average Precision@10: {results['avg_precision_10']:.3f}")
    print(f"Average Relevancy:    {results['avg_relevancy']:.3f}")
    print(f"Category Accuracy:    {results['category_accuracy']:.1%}")
