# High-Precision & Scalable Graph-RAG Engine Roadmap

Core architectural blueprint strictly focused on **Retrieval Quality (Precision/Grounding)** and **System Scalability (Throughput/Concurrency)** for enterprise-scale knowledge graphs and hybrid vector retrieval.

Strict Invariants:
- Hexagonal Architecture (`contracts`, `domain`, `infrastructure`, `service`, `tests`)
- 3-Gate Data Integrity Model (Ingress Gate, Domain Invariants, Storage Authority)
- Zero-comment rule in function bodies
- Immutable, typed parameter design
- Distributed non-blocking concurrency (zero stateful in-memory bottleneck)

---

## Pillar I: Retrieval Quality & Knowledge Graph Precision

- [ ] **Task 01: AST-Aware Semantic Chunking**
  - Implement syntax-aware chunking in `src/features/parse/` using polyglot tree-sitter parsers.
  - Guarantee class, function, and SQL block boundaries are never severed mid-declaration, preserving contextual integrity.

- [ ] **Task 02: Deterministic Entity Resolution & Deduplication**
  - Build pure normalization and entity deduplication rules in `src/features/chunk_dedup/` and `src/features/data_integrity/`.
  - Resolve aliased, canonical, and fully qualified symbols into unified entity nodes before persistence.

- [ ] **Task 03: Bidirectional Relationship Graph (Call & Import Graph)**
  - Construct explicit, typed graph relations: `CALLS`, `INHERITS`, `IMPORTS`, `WRITES_TABLE`, and `ENFORCES_POLICY`.
  - Enable 2-hop topological traversal to retrieve multi-tier architectural context that flat vectors miss.

- [ ] **Task 04: Hierarchical Summarization Trees (RAPTOR Core)**
  - Implement recursive clustering trees summarizing leaf code into class summaries, and classes into module architecture summaries.
  - Route high-level queries to root summaries and specific implementation queries to leaf code.

- [ ] **Task 05: Cross-Encoder Neural Reranking with Calibrated Cutoffs**
  - Connect `BAAI/bge-reranker-large` or Cohere Rerank v3 in `src/features/rerank/`.
  - Enforce strict confidence threshold gates to drop low-scoring noise before context reaches the generation stage.

- [ ] **Task 06: Self-Correction & Pre-Generation Context Verification**
  - Build a verification rule in `src/features/output_guard/` checking if the retrieved context explicitly satisfies all named query entities.
  - Trigger automatic query expansion hops if required entity evidence is absent.

- [ ] **Task 07: Dense + Sparse + Graph Hybrid Fusion (Weighted RRF)**
  - Implement Reciprocal Rank Fusion (RRF) combining dense semantic embeddings (BGE-M3), lexical sparse vectors (SPLADE/BM25), and graph topological distance.
  - Prevent lexical-only or dense-only bias from degrading precision.

- [ ] **Task 08: Automated Citation Grounding & Hallucination Gate**
  - Enforce strict quotation and citation verification in `src/features/output_guard/`.
  - Automatically strip or flag ungrounded statements before returning the final response envelope.

- [ ] **Task 09: Query Intent Decomposition & Disambiguation**
  - Parse multi-part questions into atomic sub-queries with independent retrieval pipelines, synthesizing context across topics.

- [ ] **Task 10: Dynamic Index-Level Filtering via ACL & Version Tags**
  - Apply multi-tenant partition filters and version boundary conditions directly inside Qdrant and Neo4j queries to prevent stale data contamination.

- [ ] **Task 11: Negative Constraint & Anti-Pattern Indexing**
  - Index architectural constraints, deprecated APIs, and forbidden patterns as distinct negative-constraint graph nodes.

- [ ] **Task 12: Context Redundancy Pruning & Compression**
  - Apply token-level deduping across retrieved chunks to maximize effective prompt context density and eliminate duplicate sentences.

- [ ] **Task 13: Automated Golden Benchmark Evaluation Harness**
  - Build an automated evaluation suite running 100 golden queries measuring Hit@K, MRR, and NDCG to prevent quality regression during iterations.

---

## Pillar II: System Scalability, Concurrency & Throughput

- [ ] **Task 14: Distributed Qdrant HNSW Sharding & Multi-Tenancy**
  - Tune collection partitions, tenant-scoped indexing, and HNSW parameters (`m`, `ef_construct`, `ef_search`) for sub-15ms search across 10M+ vectors.

- [ ] **Task 15: Asynchronous Ingestion via Kafka & Worker Pool**
  - Offload heavy document parsing, vector embedding, and graph indexing to Kafka consumer workers with backpressure management.

- [ ] **Task 16: Multi-Tier Distributed Cache (Valkey / Redis L1/L2)**
  - Implement caching in `src/infra/cache/` for query embeddings, reranking scores, and final responses with automatic invalidation on updates.

- [ ] **Task 17: Dynamic Batched Embedding Generation**
  - Batch individual chunk embedding requests into dynamic micro-batches (e.g. 32 chunks / 20ms) via Text Embeddings Inference (TEI) to saturate GPU tensors.

- [ ] **Task 18: Non-Blocking Database Adapter (`asyncpg`)**
  - Replace in-memory storage adapters with an `asyncpg` pooled connection manager executing parameterized `FLOW_*` SQL queries with strict timeouts.

- [ ] **Task 19: Zero-Copy Stream Processing for Ingestion**
  - Process multi-megabyte files through chunked streaming iterators to prevent memory spikes on large codebases and documents.

- [ ] **Task 20: Graph Traversal Depth & Timeout Circuit Breaker**
  - Guard Cypher graph traversals with maximum depth limits (max 2–3 hops) and timeouts to prevent combinatorial explosions under circular dependencies.

- [ ] **Task 21: Zero-Downtime Blue/Green Vector & Graph Aliasing**
  - Implement atomic collection aliasing in Qdrant and Neo4j so index rebuilding occurs in shadow mode without interrupting live reads.

- [ ] **Task 22: Leaky-Bucket Rate Limiting & Token Concurrency Throttling**
  - Add tenant-level rate limiting to protect LLM endpoints and embedding services from noisy neighbors.

- [ ] **Task 23: Distributed W3C Trace Context & Metric Export**
  - Propagate W3C `traceparent` across Kafka events, HTTP requests, and background tasks, reporting p95/p99 latency per stage to Prometheus and Langfuse.

- [ ] **Task 24: Incremental CDC (Change Data Capture) Re-Indexing**
  - Ingest database WAL streams or Git diffs via `src/features/change_feed/` to re-index only dirty entities and updated relationships.

- [ ] **Task 25: Horizontal Worker Auto-Scaling Hooks**
  - Expose Kubernetes health and queue-depth probes (`/readyz`, `/metrics`) to trigger horizontal pod autoscaling under ingestion load spikes.
