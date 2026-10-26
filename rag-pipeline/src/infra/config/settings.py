"""
Centralized Configuration Loader and Validator.
"""
from typing import Optional, Tuple
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="info")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    API_VERSION: str = Field(default="v1")
    SERVICE_NAME: str = Field(default="rag-pipeline")

    DATABASE_HOST: str = Field(default="localhost")
    DATABASE_PORT: int = Field(default=5433)
    DATABASE_NAME: str = Field(default="rag_pipeline_db")
    DATABASE_USER: str = Field(default="postgres")
    DATABASE_PASSWORD: str = Field(default="password")
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5433/rag_pipeline_db"
    )
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=10)
    DATABASE_TIMEOUT_MS: int = Field(default=5000)

    OTEL_SERVICE_NAME: str = Field(default="rag-pipeline")
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="http://localhost:4317")
    LANGFUSE_PUBLIC_KEY: Optional[str] = Field(default=None)
    LANGFUSE_SECRET_KEY: Optional[str] = Field(default=None)
    LANGFUSE_HOST: str = Field(default="http://localhost:3000")

    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092")
    KAFKA_TOPIC_CHANGE_FEED: str = Field(default="rag.cdc.change-feed.v1")
    KAFKA_TOPIC_INGESTION: str = Field(default="rag.ingestion.v1")
    KAFKA_CONSUMER_GROUP: str = Field(default="rag-pipeline-workers")

    QDRANT_HOST: str = Field(default="localhost")
    QDRANT_PORT: int = Field(default=6333)
    QDRANT_COLLECTION_NAME: str = Field(default="rag_corpus_v1")

    VALKEY_URL: str = Field(default="redis://localhost:6379/0")
    VALKEY_TTL_SECONDS: int = Field(default=3600)

    EMBEDDING_SERVE_URL: str = Field(default="http://localhost:8081")
    RERANKER_SERVE_URL: str = Field(default="http://localhost:8082")

    GENERATION_ENGINE: str = Field(default="vllm")
    VLLM_ENDPOINT: str = Field(default="http://localhost:8000/v1")
    GENERATION_MODEL: str = Field(default="Qwen/Qwen2.5-7B-Instruct")
    GENERATION_MAX_TOKENS: int = Field(default=1024)
    GENERATION_TEMPERATURE: float = Field(default=0.0)
    GENERATION_TIMEOUT_SECONDS: float = Field(default=3.0)

    DEFAULT_ALLOWED_ACLS: Tuple[str, ...] = Field(default=("INTERNAL", "PUBLIC"))


settings = AppSettings()
