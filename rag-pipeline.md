A single diagram can't hold every failure mode and stay readable, so I've split the work. The diagram shows the structure and where each production control attaches. The text below follows the same stages and holds the detail.

The uncomfortable part first:  the bottom row of that diagram is where production RAG succeeds or fails. Retrieval quality is a tuning problem. Permissions, re-indexing and regression detection are design problems, and they're expensive to retrofit.

**1. Change feed**

 If your sources change, indexing is an incremental stream, not a nightly batch: source change → re-parse → re-chunk → upsert or delete by document ID.

 Deletes and ACL changes must flow through the same path as edits. A source deletion has to remove its chunks, invalidate any caches holding answers built from them, and scrub logs if they store content. Orphaned chunks are the usual failure, and "right to be forgotten" requests will find them.

**2. Parse**

 Naive text extraction scrambles tables, multi-column PDFs and scanned pages. Everything downstream then retrieves garbage confidently. Spot-check parsed output on real documents before tuning anything else.

**3. Chunk + dedup**

 Structure-aware splitting (headings, sections, code blocks) beats fixed token windows for most corpora. Carry the section title and document metadata into every chunk, because "the limit is 50" with no subject can't be retrieved. [Guessing] 300–800 tokens with light overlap is a reasonable starting band. Your eval set should pick the final number.

 Near-duplicates (v1, v2, final_v2 of the same policy) crowd out top-k and produce contradictory answers. Dedup here and mark which version is current, so ranking can prefer it.

 Make chunk IDs deterministic (doc ID + version + offset). Otherwise every re-index breaks citations, eval labels and feedback joins.

**4. Embed + enrich**

 Store dense vectors and a sparse/BM25 representation together. Dense misses exact identifiers, SKUs, error codes and names. Sparse misses paraphrase. Attach ACLs, tenant, timestamps and source IDs as filterable metadata now, because retrofitting them means a full re-index.

**5. Index**

 Changing the embedding model means re-embedding the whole corpus. Vectors from different models aren't comparable, so you can't mix them. Version indexes from day one: build the new one in parallel, shadow-evaluate it, cut over, and keep the old one for rollback. On a large corpus, that backfill is a capacity-planning event, not a config change.

 Filtered ANN search degrades badly under highly selective filters (one tenant out of thousands, a narrow date range). HNSW-style indexes can return far fewer than k results, or quietly lose recall. Test with your real filter distribution, and give large tenants their own partitions.

**6. Authz + rewrite**

Resolve the caller's permission scope before anything else touches the index. Rewrite conversational follow-ups into standalone queries, and route to the right index or skip retrieval when it isn't needed.  Skipping the rewrite LLM call on first-turn queries saves latency for little quality loss.

 If you add a semantic cache, key it on permission scope. Two users with different ACLs must never share a cached answer.

**7. Retrieve**

 Pull a generous top-k (30–100) from both dense and sparse and fuse with reciprocal rank fusion.  Apply ACL and tenant filters inside the vector query, never after. Post-filtering leaks data through logs, rerankers and caches, and silently empties top-k when the filter removes most results.

**8. Rerank**

 A cross-encoder cutting to the top 5–8 is usually the highest-ROI addition after hybrid search, at roughly 50–300 ms.  More context isn't free quality: cost scales linearly, and models attend unevenly across long contexts ("lost in the middle"). A tight reranked set usually beats 30 raw chunks.

**9. Generate**

Instruct the model to answer only from the provided context, cite chunk IDs, and say explicitly when the context doesn't contain the answer.  Without that abstain path, it fills gaps from its own weights and you can't tell.

 Put the static system prompt first and the retrieved context after it, so prompt caching actually hits. Stream the output, since generation dominates latency.

 Upgrading the generation model changes behavior even with an identical prompt. Gate every model or prompt change on your eval suite, the way you'd gate a schema migration.

**10. Output guard**

 Validate citations programmatically. Every cited chunk ID must have been in the context, and ideally the cited span should support the claim. Models fabricate plausible citation IDs.

 Strip or neutralize markdown links and images if you render output. Image URLs are a known channel for exfiltrating data through injected instructions.

**Security (cross-cutting)**

 Retrieved documents are untrusted input. A document that says "ignore previous instructions" is a prompt injection your own index delivered. Keep retrieved text structurally separated as data in the prompt. Never give a RAG agent side-effecting tools without an independent authorization check on each action.

**Evals (cross-cutting)**

 Measure retrieval and answers separately. For retrieval, use recall@k and MRR against labeled queries. For answers, measure faithfulness to the retrieved context and whether the answer actually addresses the question. If you only score end answers, you can't tell whether a regression came from chunking, retrieval, reranking or the prompt.

 The queries you designed for aren't the ones you'll get. Rebuild the golden set from real traffic in the first weeks, and keep refreshing it.

 LLM-as-judge favors longer, confident answers and shares blind spots with the generator. Calibrate it against human labels on a sample before trusting the numbers.

 Track the abstain rate ("insufficient context") as a first-class metric. If it drifts toward zero, the model is probably filling gaps.

 Thumbs up/down feedback is too sparse and noisy to be a metric. Use it to find examples worth labeling.

**Observability (cross-cutting)**

 Trace per request: the rewritten query, chunk IDs with scores at each stage, the reranked set, prompt token count, the answer, its citations, and latency per stage. Without stage-level traces, every quality complaint becomes guesswork.

 Those traces contain document content and user queries, so they inherit the strictest classification in your corpus. Set retention and access controls to match.

**Latency budget**

 Rough shape: rewrite (one LLM call, often skippable) + retrieval (tens of ms) + rerank (50–300 ms) + generation (seconds, driven by output length). Rerank and generation are where to spend optimization effort. Retrieval is rarely the bottleneck.

The question from last time still decides what bites you first: is this single-tenant or multi-tenant, and how often does the corpus change? Multi-tenant plus frequent change makes sections 1, 5 and 7 your launch blockers. Static single-tenant makes evals the main risk.