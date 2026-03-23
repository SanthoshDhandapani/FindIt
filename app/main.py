import hashlib
import json
import logging
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import router
from app.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="E-Commerce Search Engine",
    description="Multimodal product search using CrewAI agents + Pinecone hybrid retrieval",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# CORS middleware — allow React UI origin
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request latency middleware — logs timing for every request
# ---------------------------------------------------------------------------
class LatencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Latency-Ms"] = f"{latency_ms:.2f}"
        logger.info("%s %s — %.2fms", request.method, request.url.path, latency_ms)
        return response


app.add_middleware(LatencyMiddleware)


# ---------------------------------------------------------------------------
# Redis cache middleware — caches search responses
# ---------------------------------------------------------------------------
class RedisCacheMiddleware(BaseHTTPMiddleware):
    """Cache POST /api/v1/search responses in Redis.

    Cache key: hash(query + filters + sort_by)
    Default TTL: 300s (5 min)
    Sort by rating TTL: 30s (ratings change frequently)
    """

    def __init__(self, app):
        super().__init__(app)
        self._redis = None

    def _get_redis(self):
        if self._redis is None:
            try:
                import redis
                self._redis = redis.from_url(settings.redis_url)
                self._redis.ping()
            except Exception:
                self._redis = False  # Mark as unavailable
        return self._redis if self._redis else None

    async def dispatch(self, request: Request, call_next) -> Response:
        # Only cache search endpoint
        if request.url.path != "/api/v1/search" or request.method != "POST":
            return await call_next(request)

        r = self._get_redis()
        if not r:
            return await call_next(request)

        # Read body for cache key
        body = await request.body()
        cache_key = f"search:{hashlib.md5(body).hexdigest()}"

        # Check cache
        try:
            cached = r.get(cache_key)
            if cached:
                return Response(
                    content=cached,
                    media_type="application/json",
                    headers={"X-Cache": "HIT"},
                )
        except Exception:
            pass

        # Miss — run the pipeline
        response = await call_next(request)

        # Cache the response body
        if response.status_code == 200:
            try:
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                # Determine TTL
                try:
                    req_data = json.loads(body)
                    ttl = 30 if req_data.get("sort_by") == "rating" else 300
                except Exception:
                    ttl = 300

                r.setex(cache_key, ttl, response_body)

                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    media_type="application/json",
                    headers={"X-Cache": "MISS"},
                )
            except Exception:
                pass

        return response


app.add_middleware(RedisCacheMiddleware)


# Phase 3 — Guardrail middleware
# TODO: Uncomment once GuardrailMiddleware is implemented
# from app.middleware.guardrails import GuardrailMiddleware
# app.add_middleware(GuardrailMiddleware)

# Phase 3 — LangSmith tracing
if settings.langchain_tracing_v2:
    import os
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
