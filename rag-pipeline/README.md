# Enterprise Production RAG Pipeline Service

Core production implementation for the Enterprise RAG Pipeline following hexagonal modular architecture and strict policy invariants.

## Architecture Subsystems

- `config/`: Declarative configuration and environment validation schemas (`env.schema`, `.env.example`).
- `contracts/`: Versioned API contracts (OpenAPI 3.1, gRPC Proto, AsyncAPI 3.0).
- `database/`: PostgreSQL migrations, rollback scripts, Row Level Security (`rls.sql`), and schema lockfiles.
- `messaging/`: Kafka topic configurations, dead-letter queue policies (`dlq_policy.yaml`), and schemas.
- `deploy/`: Multi-stage Dockerfiles, Kubernetes manifests, Helm charts, ArgoCD configurations, and Terraform modules.
- `scripts/`: Operational scripts for running, migrating, testing, and contract code-generation.
- `src/features/`: 13 isolated hexagonal feature modules:
  - `change_feed`: CDC event ingestion and partition routing.
  - `parse`: Multi-format document parsing and layout extraction.
  - `chunk_dedup`: Token window chunking and MinHash duplicate suppression.
  - `embed_enrich`: Dense embedding calculation and metadata enrichment.
  - `index`: Vector and payload persistence in Qdrant.
  - `security`: Threat analysis, jailbreak detection, and injection mitigation.
  - `authz_rewrite`: Query authorization rewrite and tenant ACL filter injection.
  - `retrieve`: Multi-stage vector and lexical search with ACL constraints.
  - `rerank`: Cross-encoder precision scoring and candidate sorting.
  - `generate`: Citation-constrained LLM answer synthesis.
  - `output_guard`: Hallucination detection, citation verification, and PII redaction.
  - `evals`: Ragas scoring and quality evaluation harness.
  - `observability`: Distributed tracing, metrics, and audit event dispatch.
- `src/infra/`: Infrastructure clients (Qdrant, Kafka, vLLM, TEI, Valkey).
- `src/shared/`: Shared models, errors, middleware, and constants.
- `tests/`: Comprehensive test suite across unit, integration, and e2e boundaries.

## Verification

```bash
python3 -m pytest
```
