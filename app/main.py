from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="E-Commerce Search Engine",
    description="Multimodal product search using CrewAI agents + Pinecone hybrid retrieval",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")

# TODO: Add Redis cache middleware
# TODO: Add request latency middleware
# TODO: Add CORS middleware if needed

# Phase 3 — Guardrail middleware
# Pattern: Guardrails / Tripwire (Agentic Deployment)
# TODO: Uncomment once GuardrailMiddleware is implemented
# from app.middleware.guardrails import GuardrailMiddleware
# app.add_middleware(GuardrailMiddleware)

# Phase 3 — LangSmith tracing
# Pattern: Observability (Observability/CrewAI_Langsmith.py)
# TODO: Enable LangSmith tracing when LANGCHAIN_TRACING_V2=true in .env
# from app.config import settings
# if settings.langchain_tracing_v2:
#     import os
#     os.environ["LANGCHAIN_TRACING_V2"] = "true"
#     os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
#     os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
