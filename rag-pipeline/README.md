# Production RAG Pipeline

Architecture and production controls based on [rag-pipeline.md](file:///home/btpl-lap-22/live/rag-pipeline/rag-pipeline.md).

## Production Open-Source Stack Matrix

| Layer | Component | License | How it scales out |
|---|---|---|---|
| **Change feed** | Debezium → Kafka | Apache 2.0 | Partitions plus consumer groups |
| **Parse** | Docling (Unstructured OSS fallback) | MIT / Apache 2.0 | Stateless CPU/GPU workers pulling from Kafka |
| **Pipeline framework** | Haystack | Apache 2.0 | Stateless query-service pods |
| **Embedding model** | BGE-M3 or Qwen3-Embedding | MIT / Apache 2.0 | — |
| **Embedding + rerank serving** | Hugging Face TEI | Apache 2.0 | GPU pods behind HPA |
| **Rerank model** | bge-reranker-v2-m3 or Qwen3-Reranker | Apache 2.0 | Same TEI pool, or a dedicated one |
| **Index** | Qdrant (distributed mode) or OpenSearch | Apache 2.0 | Shards plus replicas |
| **Generation model** | Qwen3 or gpt-oss | Apache 2.0 | — |
| **Generation serving** | vLLM | Apache 2.0 | GPU pods, tensor parallel for large models |
| **Cache** | Valkey | BSD | Cluster mode |
| **Guardrails** | NeMo Guardrails | Apache 2.0 | Sidecar or service |
| **Evals** | Ragas | Apache 2.0 | Runs as a CI job |
| **Tracing** | Langfuse (MIT core) + OpenTelemetry | MIT | Stateless app; Postgres and ClickHouse behind it |
| **Orchestration** | Kubernetes + KEDA | Apache 2.0 | Autoscales workers on Kafka lag |

## Architecture & Subsystems
- `config/`: Declarative configuration and environment schemas (`env.schema`, `.env.example`).
- `contracts/`: Versioned API contracts (OpenAPI, gRPC proto, AsyncAPI).
- `database/`: Migrations, schemas, seeds, connection engine.
- `messaging/`: Topics, schemas, and consumer/producer engines.
- `deploy/`: Docker, Kubernetes manifests, Helm charts, Terraform, and KEDA ScaledObjects.
- `src/features/`: Hexagonal isolated features:
  - `change-feed`
  - `parse`
  - `chunk-dedup`
  - `embed-enrich`
  - `index`
  - `authz-rewrite`
  - `retrieve`
  - `rerank`
  - `generate`
  - `output-guard`
  - `security`
  - `evals`
  - `observability`
- `src/infra/`: Infrastructure clients (Qdrant, Kafka, vLLM, TEI, Valkey, Langfuse/OTel).
- `src/shared/`: Pure deterministic logic, constants, types, errors, and middleware.
