from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Core
    gemini_api_key: str
    pinecone_api_key: str
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "ecommerce-search"
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/ecommerce"
    redis_url: str = "redis://localhost:6379"
    hf_token: str = ""

    # LLM
    gemini_model: str = "gemini-2.5-flash"

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimensions: int = 384

    # Observability (Phase 1 + Phase 3)
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "ecommerce-search"

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    # Phase 3 — Reflection loop
    reflection_relevancy_threshold: float = 0.4
    reflection_max_retries: int = 2

    # Phase 3 — Guardrails
    guardrail_max_query_length: int = 500
    guardrail_rate_limit_per_minute: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
