from app.models.schemas import ParsedIntent, SearchRequest


def parse_intent_with_llm(query: str, request: SearchRequest) -> ParsedIntent:
    # TODO: LLM call (gpt-4o-mini) with JSON output schema
    # Extract: category, brand, color, price_min, price_max, sort_by, keywords, specificity
    # Override with any explicit filters passed in request
    raise NotImplementedError


def decide_alpha(intent: ParsedIntent) -> float:
    # TODO: Return alpha blend value based on intent.specificity
    # high specificity (exact model)  → 0.2  (keyword-heavy)
    # low specificity (descriptive)   → 0.85 (semantic-heavy)
    # medium (default)                → 0.6  (balanced hybrid)
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


def build_query_analyst():
    # TODO: Return CrewAI Agent with role="Query Analyst"
    raise NotImplementedError


def build_search_strategist():
    # TODO: Return CrewAI Agent with role="Search Strategist"
    raise NotImplementedError


def build_results_ranker():
    # TODO: Return CrewAI Agent with role="Results Ranker"
    raise NotImplementedError
