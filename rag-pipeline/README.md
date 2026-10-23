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

---

## Academic References & Research Foundations

- **RAG**: Lewis et al. (2020), *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, [arXiv:2005.11401](https://arxiv.org/abs/2005.11401).
- **Dense Retrieval**: Karpukhin et al. (2020), *Dense Passage Retrieval (DPR)*, [arXiv:2004.04906](https://arxiv.org/abs/2004.04906).
- **RRF Fusion**: Cormack et al. (2009), *Reciprocal Rank Fusion*, [DOI:10.1145/1571941.1572114](https://doi.org/10.1145/1571941.1572114).
- **Embeddings**: Chen et al. (2024), *BGE-M3: Multi-Lingual, Multi-Granularity Text Embeddings*, [arXiv:2402.03216](https://arxiv.org/abs/2402.03216).
- **Cross-Encoder Reranking**: Nogueira & Cho (2019), *Passage Re-ranking with BERT*, [arXiv:1901.04085](https://arxiv.org/abs/1901.04085).
- **High-Throughput Serving**: Kwon et al. (2023), *PagedAttention / vLLM*, [arXiv:2309.06180](https://arxiv.org/abs/2309.06180).
- **Evaluation**: Es et al. (2024), *Ragas: Automated Evaluation of RAG*, [arXiv:2309.15217](https://arxiv.org/abs/2309.15217).
