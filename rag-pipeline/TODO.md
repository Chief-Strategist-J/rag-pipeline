# Production Graph-RAG Engine Roadmap: 25 Critical Tasks

Architectural blueprint for building a high-performance Knowledge Graph + Hybrid Vector RAG system designed for IDEs (Claude Code, Cursor, Windsurf, VSCode) and multi-model execution.

Strictly adheres to:
- Hexagonal Architecture (`contracts`, `domain`, `infrastructure`, `service`, `tests`)
- 3-Gate Data Integrity Model (Ingress, Domain Invariants, Storage Authority)
- Zero-comment rule in function bodies
- Immutable, typed parameter design

---

## Phase I: Code Structure & AST Knowledge Graph Extraction

- [ ] **Task 01: Tree-Sitter Polyglot Parser Service**
  - Implement an AST extraction adapter in `src/features/parse/` using `tree-sitter` (supporting Python, TypeScript, SQL).
  - Extract deterministic symbols, scopes, function calls, class definitions, and import declarations rather than raw line-based text chunks.

- [ ] **Task 02: Deterministic Entity Extraction Rules**
  - Define pure domain rules in `domain/rules/` that parse extracted symbols into discrete graph nodes: `Module`, `Class`, `Function`, `Interface`, `DBTable`, and `PolicyRule`.

- [ ] **Task 03: Graph Edge Dependency Schema**
  - Establish strict relation types: `IMPORTS`, `CALLS`, `INHERITS`, `OVERRIDES`, `WRITES_TO_TABLE`, and `ENFORCES_POLICY` with deeply immutable DTOs (`model_config = ConfigDict(extra="forbid", strict=True)`).

- [ ] **Task 04: Neo4j / Memgraph Storage Port & Adapter**
  - Scaffold abstract `GraphStorePort` in `infrastructure/ports/` and high-throughput Cypher adapter in `infrastructure/adapters/` using connection pooling to ingest and traverse graph nodes and edges.

- [ ] **Task 05: AST-to-Graph Invariant Gate**
  - Add continuous invariant validation queries (`FLOW_CHECK_GRAPH_DANGLING_NODES`, `FLOW_CHECK_CIRCULAR_DEPENDENCIES`) to reject broken entity references during ingestion following the 3-gate integrity model.

---

## Phase II: Multi-Model & Plug-and-Play Inference Infrastructure

- [ ] **Task 06: Universal Provider-Agnostic LLM Engine Adapter**
  - Replace mock adapters with an abstract `LlmInferencePort` and unified client supporting OpenAI, Anthropic Claude, Google Gemini, Ollama, and local vLLM instances without touching domain orchestrators.

- [ ] **Task 07: Dynamic Model Routing Rules**
  - Create rule tables in `domain/rules/model_routing_rules.py` inspecting token budget, task type, and query complexity to route cheap/fast models (Qwen-2.5-Coder / Claude 3.5 Haiku) for query expansion and heavy models (Claude 3.5 Sonnet / GPT-4o) for code synthesis.

- [ ] **Task 08: Real Neural Embedding Gateway (TEI & Cloud)**
  - Scaffold a resilient embedding adapter connecting to Text Embeddings Inference (TEI) running `BAAI/bge-m3` locally, with automatic fallback to OpenAI `text-embedding-3-large` or Voyage-Code embeddings.

- [ ] **Task 09: Cross-Encoder Neural Reranking Adapter**
  - Implement a hardware-accelerated reranking adapter using `BAAI/bge-reranker-large` or Cohere Rerank v3 with strict latency budgeting (<150ms).

- [ ] **Task 10: LLM Structured Output Enforcement**
  - Enforce strict JSON Schema generation on all LLM responses to prevent free-text drift and ensure predictable parsing across all consumer IDEs.

---

## Phase III: Hybrid Graph + Vector Multi-Hop Retrieval

- [ ] **Task 11: Sub-Graph Neighborhood Query Workflow**
  - Build a graph retrieval workflow that takes a seed symbol (e.g., `DataIntegrityService`) and performs 2-hop topological traversal (`node -> calls -> dependency -> enforces -> table`) to collect surrounding context that vectors miss.

- [ ] **Task 12: Reciprocal Rank Fusion (RRF) Domain Combiner**
  - Implement a pure mathematical fusion rule (`score = 1 / (60 + rank_dense) + 1 / (60 + rank_sparse) + 1 / (60 + rank_graph)`) uniting vector hits, lexical BM25 hits, and graph topological hits.

- [ ] **Task 13: Hierarchical Document & Code Summarization Trees (RAPTOR-Style)**
  - Create a clustering service that summarizes child functions into class summaries, and classes into module summaries, generating a multi-resolution knowledge graph for high-level architectural queries.

- [ ] **Task 14: Cross-Tenant Vector-Graph Partitioning**
  - Implement hard isolation where Qdrant payloads and Neo4j labels include `tenant_id` to guarantee zero cross-tenant memory leaks under selective ACL filters.

- [ ] **Task 15: Query Intent Decomposition Engine**
  - Add query decomposition workflow splitting ambiguous developer queries into parallel graph sub-queries: vector search for natural language policies + Cypher path queries for database tables.

---

## Phase IV: Universal IDE Protocols & Standardized Interfaces

- [ ] **Task 16: Production Model Context Protocol (MCP) Server**
  - Scaffold an official JSON-RPC MCP server (`src/api/mcp/` and `scripts/ide_mcp_server.py`) exposing standard IDE tools: `code_search`, `graph_inspect`, `policy_check`, and `trace_dependencies`.

- [ ] **Task 17: Language Server Protocol (LSP) Bridge**
  - Implement an LSP daemon extension allowing IDEs to query the RAG pipeline via standard hover, definition lookup, and code lens notifications without proprietary extensions.

- [ ] **Task 18: Cursor & Windsurf Rule Files Auto-Generator**
  - Build a dynamic export service compiling your high-priority database rules and hexagonal contracts into optimized `.cursorrules` and `.windsurfrules` files.

- [ ] **Task 19: Context Truncation & Token Budget Guard**
  - Implement a token budget allocator in `service/` that dynamically slices retrieved graph paths and code snippets to fit within caller IDE limits (4k, 8k, 32k window budgets) with zero dropped syntax tokens.

- [ ] **Task 20: Streaming SSE / WebSocket Delivery Gateway**
  - Add `/api/v1/pipeline/stream` supporting Server-Sent Events (SSE) so IDE completions stream tokens with sub-50ms Time-To-First-Token (TTFT) while asynchronously logging telemetry.

---

## Phase V: Enterprise Data Integrity, Verification & Continuous Learning

- [ ] **Task 21: Persistent PostgreSQL Storage Adapter for Data Integrity**
  - Replace `MemoryDataIntegrityRepositoryAdapter` with an `asyncpg` adapter executing real transactions and mapping native SQL errors (`SQLSTATE 23xxx`) to `CONSTRAINT_REGISTRY`.

- [ ] **Task 22: Automated Continuous Graph Invariant Worker**
  - Create a background daemon executing `FLOW_CHECK_*` integrity checks on a scheduled cron to report orphan symbols, broken foreign references, and ungrounded nodes.

- [ ] **Task 23: Automated Feedback & Telemetry Loop in Langfuse**
  - Ingest IDE user actions (accept/reject completion) via an audit endpoint and correlate with original Langfuse trace IDs to compute real-world retrieval precision.

- [ ] **Task 24: Incremental Codebase Git Change Feed Worker**
  - Connect `change_feed` to Git webhooks or local file watchers to incrementally re-index only changed files and updated AST edges rather than re-indexing the whole repository.

- [ ] **Task 25: Automated Negative & Golden Evaluation Dataset**
  - Build an offline benchmark suite with 50 golden codebase questions asserting that the hybrid graph-vector pipeline consistently beats pure lexical and pure vector retrieval in precision, recall, and grounding score.
