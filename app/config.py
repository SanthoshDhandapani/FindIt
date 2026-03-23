from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    pinecone_api_key: str
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "ecommerce-search"
    database_url: str
    redis_url: str = "redis://localhost:6379"
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "ecommerce-search"
    app_env: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
