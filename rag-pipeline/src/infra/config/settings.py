"""
Centralized Configuration Loader and Validator.
"""
from typing import Optional
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
    VLLM_ENDPOINT: str = Field(default="http://localhost:8000/v1")


settings = AppSettings()
