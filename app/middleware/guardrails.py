"""
Phase 3 — Input guardrails middleware.

Pattern: Guardrails / Tripwire (input validation)
Reference: Agentic Deployment guardrail patterns

Validates and sanitizes search queries before they reach the agent pipeline.
Blocks prompt injection, non-product queries, and malformed input.
"""

import re
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Patterns that indicate prompt injection attempts
BLOCKED_PATTERNS = [
    r"ignore\s+(all\s+)?instructions",
    r"system\s+prompt",
    r"forget\s+everything",
    r"you\s+are\s+now",
    r"act\s+as\s+if",
    r"disregard\s+(previous|above)",
    r"override\s+(your|the)\s+(instructions|rules)",
]

# Query length constraints
MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 500

# Rate limiting config
MAX_REQUESTS_PER_MINUTE = 30


def validate_query(query: str) -> tuple[bool, str]:
    """Validate a search query against guardrails.

    Returns (is_valid, error_message).
    If valid, error_message is empty string.
    """
    # TODO: Check query length (min/max)
    # TODO: Check against BLOCKED_PATTERNS using re.search with IGNORECASE
    # TODO: Sanitize: strip whitespace, check for empty after strip
    # TODO: Return (True, "") if all checks pass
    # TODO: Return (False, reason) if any check fails
    raise NotImplementedError


def sanitize_query(query: str) -> str:
    """Normalize and clean a search query.

    - Strip leading/trailing whitespace
    - Collapse multiple spaces
    - Remove control characters
    - Lowercase for consistency
    """
    # TODO: Apply sanitization steps
    # TODO: Return cleaned query string
    raise NotImplementedError


class GuardrailMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that validates search queries before processing.

    Only applies to POST /api/v1/search requests.
    Other endpoints pass through without validation.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # TODO: Check if request path is /api/v1/search and method is POST
        # TODO: If yes, read request body JSON and validate query field
        # TODO: If validation fails, return 400 response with error message
        # TODO: If validation passes, sanitize query and forward to next handler
        # TODO: For non-search endpoints, pass through directly
        raise NotImplementedError
