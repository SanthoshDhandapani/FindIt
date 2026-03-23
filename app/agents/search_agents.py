from app.models.schemas import ParsedIntent, SearchRequest


# ---------------------------------------------------------------------------
# Phase 1 — Core agent helper functions
# ---------------------------------------------------------------------------

def parse_intent_with_llm(query: str, request: SearchRequest) -> ParsedIntent:
    # TODO: LLM call (gpt-4o-mini) with JSON output schema
    # Extract: category, brand, color, price_min, price_max, sort_by, keywords, specificity
    # Override with any explicit filters passed in request
    raise NotImplementedError


def decide_alpha(intent: ParsedIntent) -> float:
    # TODO (Phase 1): Return alpha blend value based on intent.specificity
    #   high specificity (exact model)  → 0.2  (keyword-heavy)
    #   low specificity (descriptive)   → 0.85 (semantic-heavy)
    #   medium (default)                → 0.6  (balanced hybrid)
    #
    # TODO (Phase 3 — Category-aware routing): Use both specificity AND category
    #   Pattern: Routing (Agentic Design Patterns/Routing.py)
    #   Category base alphas:
    #     electronics → 0.3 (keyword-heavy, users search by exact specs)
    #     shoes       → 0.8 (semantic-heavy, users describe aesthetics)
    #     stationery  → 0.5 (balanced, price-sensitive)
    #     unknown     → 0.6 (fallback)
    #   Then adjust by specificity:
    #     high  → base - 0.2 (min 0.1)
    #     low   → base + 0.15 (max 0.95)
    #     medium → base as-is
    raise NotImplementedError


def build_pinecone_filter(intent: ParsedIntent) -> dict:
    # TODO: Build Pinecone metadata filter dict from intent fields
    # Fields to filter: category, brand, color, price range
    raise NotImplementedError


def compute_relevancy_score(
    similarity: float,
    rating: float,
    review_count: int,
    alpha_rating: float = 0.2,
) -> float:
    # TODO: Blend similarity + rating signal into a 0–1 relevancy score
    # Formula: (1 - alpha_rating) * similarity + alpha_rating * (rating/5) + review_boost
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Phase 1 — CrewAI agent builders
# ---------------------------------------------------------------------------

def build_query_analyst():
    # TODO: Return CrewAI Agent with role="Query Analyst"
    raise NotImplementedError


def build_search_strategist():
    # TODO: Return CrewAI Agent with role="Search Strategist"
    raise NotImplementedError


def build_results_ranker():
    # TODO: Return CrewAI Agent with role="Results Ranker"
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Phase 3 — Multi-agent handoff for compound queries
# ---------------------------------------------------------------------------
# Pattern: Multi-Agent Handoff (Agentic Design Patterns/MultiAgent.py)

def detect_multi_intent(query: str, intent: ParsedIntent) -> list[ParsedIntent]:
    """Detect compound queries that span multiple categories.

    Examples:
        "laptop and a bag for it" → [electronics intent, stationery intent]
        "running shoes and a water bottle" → [shoes intent, stationery intent]

    If the query targets a single category, returns a list with just the
    original intent. If multiple intents are detected, splits into
    sub-intents each with their own category and keywords.

    Args:
        query: Original user query string
        intent: The initial ParsedIntent from parse_intent_with_llm

    Returns:
        List of ParsedIntent objects, one per detected sub-query.
    """
    # TODO: Use LLM (gpt-4o-mini) to detect if query contains multiple intents
    # TODO: If single intent, return [intent]
    # TODO: If multiple, split query into sub-queries and parse each
    # TODO: Each sub-intent gets its own category, keywords, specificity
    raise NotImplementedError
