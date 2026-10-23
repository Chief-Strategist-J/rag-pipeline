# Production RAG Pipeline

A production-grade, open-source Retrieval-Augmented Generation (RAG) pipeline architecture designed for high availability, zero-trust network security, and horizontal scalability.

![RAG Pipeline Architecture](rag_pipeline.svg)

---

## Architecture & Technology Stack

| Layer | Component | License | Scaling Strategy |
|---|---|---|---|
| **Change feed** | Debezium → Kafka | Apache 2.0 | Partitions plus consumer groups |
| **Parse** | Docling (Unstructured OSS fallback) | MIT / Apache 2.0 | Stateless CPU/GPU workers pulling from Kafka |
| **Pipeline framework** | Haystack | Apache 2.0 | Stateless query-service pods |
| **Embedding model** | BGE-M3 or Qwen3-Embedding | MIT / Apache 2.0 | GPU pools via Hugging Face TEI |
| **Embedding + rerank serving** | Hugging Face TEI | Apache 2.0 | GPU pods behind HPA |
| **Rerank model** | bge-reranker-v2-m3 or Qwen3-Reranker | Apache 2.0 | Dedicated TEI pool |
| **Index** | Qdrant (distributed mode) | Apache 2.0 | Sharding plus replication |
| **Generation model** | Qwen3 or gpt-oss | Apache 2.0 | High-throughput LLM serving via vLLM |
| **Generation serving** | vLLM | Apache 2.0 | GPU pods, tensor parallelism |
| **Cache** | Valkey | BSD | Cluster mode with AOF/RDB recovery |
| **Guardrails** | NeMo Guardrails | Apache 2.0 | Sidecar or dedicated gateway |
| **Evals** | Ragas | Apache 2.0 | Automated CI/CD regression testing |
| **Tracing** | Langfuse + OpenTelemetry | MIT | Distributed W3C trace context, ClickHouse/PostgreSQL sink |
| **Orchestration** | Kubernetes + KEDA | Apache 2.0 | Event-driven autoscaling on Kafka consumer lag |

---

## Repository Structure

```
├── rag-pipeline.md               # Production controls, failure modes, and engineering specification
├── rag_pipeline.svg              # Architecture diagram and stage workflow
├── policies/                     # Git submodule: organizational architectural rules and policies
└── rag-pipeline/                 # Core service package root
    ├── config/                   # Declarative configuration and environment schemas
    │   └── env.schema
    ├── contracts/                # OpenAPI, gRPC Proto, and AsyncAPI specifications
    ├── database/                 # Schema migrations, seeds, and connection engine
    ├── messaging/                # Topics, event schemas, and streaming engine
    ├── deploy/                   # Deployment manifests
    │   └── docker/
    │       ├── base/             # Base hardened Dockerfile
    │       ├── service/          # Multi-stage production and dev Dockerfiles
    │       └── compose/          # Compose stacks (single, infra, polyglot)
    ├── src/
    │   ├── main.py               # Bootstrap runner with /healthz & /readyz probes
    │   ├── infra/                # Infrastructure adapters (config, clients, observability)
    │   ├── shared/               # Pure libraries (constants, types, errors, utils)
    │   └── features/             # Hexagonal feature modules
    │       ├── change-feed/
    │       ├── parse/
    │       ├── chunk-dedup/
    │       ├── embed-enrich/
    │       ├── index/
    │       ├── authz-rewrite/
    │       ├── retrieve/
    │       ├── rerank/
    │       ├── generate/
    │       ├── output-guard/
    │       ├── security/
    │       ├── evals/
    │       └── observability/
    ├── .env.example              # Centralized environment template
    └── pyproject.toml            # Package dependency manifest
```

---

## Network Security & Micro-Segmentation

The deployment topology adheres to zero-trust micro-segmentation across four isolated networks:

- **`segment-public` (`172.28.10.0/24`)**: Delivery API ingress and UI gateways.
- **`segment-internal` (`172.28.20.0/24`, `internal: true`)**: Kafka and Zookeeper streaming coordination without internet egress.
- **`segment-data` (`172.28.30.0/24`, `internal: true`)**: Qdrant vector storage and Valkey cache.
- **`segment-observability` (`172.28.40.0/24`, `internal: true`)**: PostgreSQL and Langfuse telemetry sink.

Host ports are bound to loopback (`127.0.0.1`) to prevent unintended exposure.

---

## Getting Started

### 1. Configuration
```bash
cd rag-pipeline
cp .env.example .env
```

### 2. Run Local Infrastructure
```bash
docker compose -f deploy/docker/compose/docker-compose.infra.yml up -d
```

### 3. Run Full End-to-End Stack
```bash
docker compose -f deploy/docker/compose/docker-compose.polyglot.yml up -d --build
```

### 4. Health Checks
- Liveness: `curl http://localhost:8000/healthz`
- Readiness: `curl http://localhost:8000/readyz`
- Swagger Docs: `http://localhost:8000/api/v1/docs`

---

## License

This project is licensed under the Apache 2.0 License.
