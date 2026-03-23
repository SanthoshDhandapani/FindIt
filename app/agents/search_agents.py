
from __future__ import annotations

import json
import logging

from google.genai import types

from app.config import settings
from app.db.clients import get_gemini_client
from app.models.schemas import ParsedIntent, SearchRequest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Issue #7 — LLM intent parsing
# ---------------------------------------------------------------------------

_INTENT_SYSTEM_PROMPT = """
You are a search intent parser for an e-commerce product search engine.
Extract structured search intent from the user query and return ONLY a JSON object.

JSON schema:
{
  "category":    "<electronics|shoes|clothes|stationery|null>",
  "brand":       "<brand name string or null>",
  "color":       "<color string or null>",
  "price_min":   "<number or null>",
  "price_max":   "<number or null>",
  "sort_by":     "<relevancy|rating|price_asc|price_desc>",
  "keywords":    ["<key search term>", ...],
  "specificity": "<high|medium|low>"
}

Specificity rules:
  high   → user mentions exact model, SKU, or full product name
  medium → user mentions brand + type/category
  low    → user uses descriptive or vague language

Return ONLY the JSON. No explanation, no markdown.
""".strip()


def parse_intent_with_llm(query: str, request: SearchRequest) -> ParsedIntent:
    """Parse a natural language query into a structured ParsedIntent using Gemini.

    Calls gemini-2.5-flash with a JSON output schema, then overrides any
    inferred fields with explicit filters already set on the SearchRequest.

    Args:
        query:   Raw user search string
        request: Original SearchRequest (may carry explicit category/brand/etc.)

    Returns:
        ParsedIntent with all extractable fields populated
    """
    prompt = f'User query: "{query}"'

    try:
        response = get_gemini_client().models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=_INTENT_SYSTEM_PROMPT,
                response_mime_type="application/json",
            ),
        )
        data = json.loads(response.text)
    except Exception as exc:
        logger.warning("Gemini intent parse failed (%s) — using fallback", exc)
        data = {}

    # Build intent from LLM output, with sensible defaults
    intent = ParsedIntent(
        category=data.get("category"),
        brand=data.get("brand"),
        color=data.get("color"),
        price_min=data.get("price_min"),
        price_max=data.get("price_max"),
        sort_by=data.get("sort_by", "relevancy"),
        keywords=data.get("keywords", []),
        specificity=data.get("specificity", "medium"),
    )

    # Explicit filters from SearchRequest always override LLM inference
    if request.category:
        intent.category = request.category
    if request.brand:
        intent.brand = request.brand
    if request.color:
        intent.color = request.color
    if request.price_min is not None:
        intent.price_min = request.price_min
    if request.price_max is not None:
        intent.price_max = request.price_max
    if request.sort_by != "relevancy":
        intent.sort_by = request.sort_by

    return intent


# ---------------------------------------------------------------------------
# Issue #8 — Search strategy helpers
# ---------------------------------------------------------------------------

def decide_alpha(intent: ParsedIntent) -> float:
    """Return the semantic/keyword blend weight based on query specificity.

    Alpha controls the RRF merge:
        alpha → 1.0 = pure semantic
        alpha → 0.0 = pure keyword

    Phase 1 (specificity-only):
        high   → 0.2  (keyword-heavy — user knows exact product)
        medium → 0.6  (balanced hybrid)
        low    → 0.85 (semantic-heavy — user is describing, not naming)

    Phase 3 (category-aware routing):
        Uses category base alpha then adjusts by specificity.

    Args:
        intent: ParsedIntent from parse_intent_with_llm

    Returns:
        float in range [0.0, 1.0]
    """
    specificity_alpha = {
        "high":   0.2,
        "medium": 0.6,
        "low":    0.85,
    }
    return specificity_alpha.get(intent.specificity, 0.6)


def build_pinecone_filter(intent: ParsedIntent) -> dict:
    """Build a Pinecone metadata filter dict from intent fields.

    Constructs $eq / $gte / $lte filter conditions for category, brand,
    color, and price range using Pinecone filter syntax.

    Args:
        intent: ParsedIntent with optional filter fields

    Returns:
        dict: Pinecone-compatible metadata filter, or {} if no filters apply
    """
    filters: dict = {}

    if intent.category:
        filters["category"] = {"$eq": intent.category}
    if intent.brand:
        filters["brand"] = {"$eq": intent.brand.lower()}
    if intent.color:
        filters["color"] = {"$eq": intent.color.lower()}
    if intent.price_min is not None:
        filters["price"] = {**filters.get("price", {}), "$gte": intent.price_min}
    if intent.price_max is not None:
        filters["price"] = {**filters.get("price", {}), "$lte": intent.price_max}

    return filters


def compute_relevancy_score(
    similarity: float,
    rating: float,
    review_count: int,
    alpha_rating: float = 0.2,
) -> float:
    """Blend vector similarity with product rating and popularity signal.

    Formula:
        review_boost = min(review_count / 1000, 1.0) * 0.05
        score = (1 - alpha_rating) * similarity
              + alpha_rating * (rating / 5)
              + review_boost

    Result is clamped to [0.0, 1.0].

    Args:
        similarity:   Cosine similarity from Pinecone (0–1)
        rating:       Product rating (0–5)
        review_count: Number of reviews
        alpha_rating: Weight given to rating vs similarity (default 0.2)

    Returns:
        float: Blended relevancy score in [0.0, 1.0]
    """
    review_boost = min(review_count / 1000, 1.0) * 0.05
    score = (
        (1 - alpha_rating) * similarity
        + alpha_rating * (rating / 5)
        + review_boost
    )
    return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# Phase 1 — CrewAI agent builders (Issue #9)
# ---------------------------------------------------------------------------

from crewai import Agent, Task, Crew, LLM, Process


def _get_llm() -> LLM:
    """Return a CrewAI LLM configured for Gemini via LiteLLM."""
    return LLM(
        model=f"gemini/{settings.gemini_model}",
        max_completion_tokens=512,
    )


def build_query_analyst() -> Agent:
    """CrewAI Agent: parses user query into structured intent."""
    return Agent(
        role="Query Analyst",
        goal="Extract structured search intent (category, brand, color, price, specificity) from the user query.",
        backstory=(
            "You are an expert at understanding e-commerce search queries. "
            "You extract the user's true intent — what category they want, "
            "which brand, color preference, price range, and how specific their query is. "
            "You always output structured JSON matching the ParsedIntent schema."
        ),
        llm=_get_llm(),
        verbose=False,
    )


def build_search_strategist() -> Agent:
    """CrewAI Agent: decides search strategy (alpha, filters, namespace)."""
    return Agent(
        role="Search Strategist",
        goal="Decide the optimal search mode (semantic vs keyword blend) and build metadata filters based on the parsed intent.",
        backstory=(
            "You are a search systems expert. Given a parsed query intent, "
            "you decide the alpha weight for hybrid search — high specificity "
            "queries get keyword-heavy search, vague queries get semantic-heavy search. "
            "You also construct Pinecone metadata filters for brand, color, and price."
        ),
        llm=_get_llm(),
        verbose=False,
    )


def build_results_ranker() -> Agent:
    """CrewAI Agent: re-ranks search results by blending similarity, rating, and reviews."""
    return Agent(
        role="Results Ranker",
        goal="Re-score and rank product search results by blending semantic similarity with product rating and review count into a final relevancy score.",
        backstory=(
            "You are a ranking specialist. You take raw search candidates and "
            "compute a final relevancy score that balances how well the product "
            "matches the query (similarity) with social proof (rating, reviews). "
            "Your scoring formula ensures the best products surface to the top."
        ),
        llm=_get_llm(),
        verbose=False,
    )


def build_search_crew() -> Crew:
    """Build the 3-agent CrewAI crew for the search pipeline.

    Agents run sequentially:
        Query Analyst → Search Strategist → Results Ranker

    Returns:
        Crew ready to kickoff with inputs={"query": "..."}
    """
    analyst = build_query_analyst()
    strategist = build_search_strategist()
    ranker = build_results_ranker()

    task_analyze = Task(
        description=(
            "Parse the user search query: '{query}'\n"
            "Extract: category, brand, color, price_min, price_max, sort_by, keywords, specificity.\n"
            "Return a JSON object matching the ParsedIntent schema."
        ),
        expected_output="A JSON object with category, brand, color, price range, keywords, and specificity.",
        agent=analyst,
    )

    task_strategize = Task(
        description=(
            "Given the parsed intent from the Query Analyst, decide:\n"
            "1. Alpha value (0.0-1.0) for semantic/keyword blend\n"
            "2. Pinecone metadata filters (category, brand, color, price range)\n"
            "3. Which namespace(s) to search\n"
            "Rules: high specificity → alpha=0.2, medium → 0.6, low → 0.85"
        ),
        expected_output="A JSON with alpha value, filters dict, and target namespaces.",
        agent=strategist,
    )

    task_rank = Task(
        description=(
            "Given search candidates with similarity scores and product metadata, "
            "compute a final relevancy score for each result using:\n"
            "  score = (1 - 0.2) * similarity + 0.2 * (rating/5) + min(review_count/1000, 1.0) * 0.05\n"
            "Return results sorted by relevancy score descending."
        ),
        expected_output="A ranked list of products with relevancy scores.",
        agent=ranker,
    )

    return Crew(
        agents=[analyst, strategist, ranker],
        tasks=[task_analyze, task_strategize, task_rank],
        process=Process.sequential,
        verbose=False,
    )


# ---------------------------------------------------------------------------
# Phase 3 — Multi-agent handoff for compound queries
# ---------------------------------------------------------------------------

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
    # TODO: Use Gemini to detect if query contains multiple intents
    # TODO: If single intent, return [intent]
    # TODO: If multiple, split query into sub-queries and parse each
    raise NotImplementedError
