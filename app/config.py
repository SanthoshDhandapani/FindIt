from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Core
    openai_api_key: str
    pinecone_api_key: str
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "ecommerce-search"
    database_url: str
    redis_url: str = "redis://localhost:6379"

    # Observability (Phase 1 + Phase 3)
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "ecommerce-search"

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    # Phase 3 — HuggingFace embedding fallback
    embedding_provider: str = "openai"  # "openai" | "huggingface"
    hf_embedding_model: str = "all-MiniLM-L6-v2"

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
