import time
from typing import Dict, Any, Sequence
from src.features.authz_rewrite.service.authz_rewrite_service import AuthzRewriteService, AuthzRewriteServiceDeps
from src.features.authz_rewrite.contracts.authz_rewrite_types import RewriteInputDTO, ConversationTurn
from src.features.authz_rewrite.infrastructure.adapters.authz_rewrite_repository_adapter import (
    MemoryAuthzPermissionAdapter,
    VllmQueryRewriteAdapter,
)

from src.features.embed_enrich.service.embed_enrich_service import EmbedEnrichService, EmbedEnrichServiceDeps
from src.features.embed_enrich.contracts.embed_enrich_types import EmbeddingRequestDTO
from src.features.embed_enrich.infrastructure.adapters.embed_enrich_adapters import (
    BgeM3EmbeddingAdapter,
    LexicalSparseEncodingAdapter,
)

from src.features.retrieve.service.retrieve_service import RetrieveService, RetrieveServiceDeps
from src.features.retrieve.contracts.retrieve_types import RetrieveRequestDTO
from src.features.retrieve.infrastructure.adapters.retrieve_adapters import MemoryHybridVectorSearchAdapter

from src.features.rerank.service.rerank_service import RerankService, RerankServiceDeps
from src.features.rerank.contracts.rerank_types import RerankRequestDTO
from src.features.rerank.infrastructure.adapters.rerank_adapters import BgeRerankerAdapter

from src.features.generate.service.generate_service import GenerateService, GenerateServiceDeps
from src.features.generate.contracts.generate_types import GenerationRequestDTO
from src.features.generate.infrastructure.adapters.generate_adapters import VllmQwenGeneratorAdapter

from src.features.security.service.security_service import SecurityService, SecurityServiceDeps
from src.features.security.contracts.security_types import SecurityInspectionRequestDTO
from src.features.security.infrastructure.adapters.security_adapters import MemoryThreatDetectionAdapter

from src.features.output_guard.service.output_guard_service import OutputGuardService, OutputGuardServiceDeps
from src.features.output_guard.contracts.output_guard_types import GuardInspectionRequestDTO
from src.features.output_guard.infrastructure.adapters.output_guard_adapters import MemoryGuardAuditAdapter

from src.features.observability.service.observability_service import ObservabilityService, ObservabilityServiceDeps
from src.features.observability.contracts.observability_types import RequestTelemetryEnvelopeDTO, PipelineStageMetricsDTO
from src.features.observability.infrastructure.adapters.observability_adapters import MemoryTelemetryCollectorAdapter

from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError
from src.shared.utils.time_utils import utc_now_iso


class EndToEndPipelineOrchestrator:
    def __init__(self, seeded_points=()) -> None:
        self.authz_service = AuthzRewriteService(
            type("AuthzDeps", (), {
                "authz_port": MemoryAuthzPermissionAdapter(),
                "rewrite_port": VllmQueryRewriteAdapter("http://127.0.0.1:8000", "Qwen2.5")
            })()
        )
        self.security_service = SecurityService(
            type("SecurityDeps", (), {
                "threat_port": MemoryThreatDetectionAdapter()
            })()
        )
        self.embed_service = EmbedEnrichService(
            type("EmbedDeps", (), {
                "dense_port": BgeM3EmbeddingAdapter(128),
                "sparse_port": LexicalSparseEncodingAdapter()
            })()
        )
        self.vector_search_adapter = MemoryHybridVectorSearchAdapter(seeded_points)
        self.retrieve_service = RetrieveService(
            type("RetrieveDeps", (), {
                "search_port": self.vector_search_adapter
            })()
        )
        self.rerank_service = RerankService(
            type("RerankDeps", (), {
                "model_port": BgeRerankerAdapter()
            })()
        )
        self.generate_service = GenerateService(
            type("GenDeps", (), {
                "llm_port": VllmQwenGeneratorAdapter()
            })()
        )
        self.guard_service = OutputGuardService(
            type("GuardDeps", (), {
                "audit_port": MemoryGuardAuditAdapter()
            })()
        )
        self.obs_collector = MemoryTelemetryCollectorAdapter()
        self.obs_service = ObservabilityService(
            type("ObsDeps", (), {
                "collector_port": self.obs_collector
            })()
        )

    async def execute_query(
        self,
        tenant_id: str,
        user_id: str,
        query: str,
        conversation_history: Sequence[ConversationTurn],
        request_id: str,
        trace_id: str
    ) -> Result[Dict[str, Any], ApplicationError]:
        t0 = time.perf_counter()
        stages = []

        # 1. Authz + Rewrite
        s1_start = time.perf_counter()
        rewrite_res = await self.authz_service.execute(
            RewriteInputDTO(
                query=query,
                tenantId=tenant_id,
                userId=user_id,
                conversationHistory=conversation_history,
                skipRewriteIfFirstTurn=True
            )
        )
        s1_dur = (time.perf_counter() - s1_start) * 1000.0
        if not rewrite_res.is_ok:
            return Err(rewrite_res.error)
        authz_out = rewrite_res.value
        stages.append(PipelineStageMetricsDTO(stageName="authz_rewrite", durationMs=s1_dur, status="OK"))

        # 2. Embed
        s2_start = time.perf_counter()
        embed_res = await self.embed_service.generate_embeddings(
            EmbeddingRequestDTO(
                tenantId=tenant_id,
                documentId="query-embed",
                version=1,
                aclTags=authz_out.permissionScope.allowedAcls,
                chunks=[{"content": authz_out.rewrittenQuery}],
                correlationId=request_id
            )
        )
        s2_dur = (time.perf_counter() - s2_start) * 1000.0
        if not embed_res.is_ok:
            return Err(embed_res.error)
        q_vec = embed_res.value.vectors[0]
        stages.append(PipelineStageMetricsDTO(stageName="embed", durationMs=s2_dur, status="OK"))

        # 3. Retrieve
        s3_start = time.perf_counter()
        retrieve_res = await self.retrieve_service.retrieve_candidates(
            RetrieveRequestDTO(
                tenantId=tenant_id,
                query=authz_out.rewrittenQuery,
                denseVector=q_vec.denseVector,
                sparseIndices=q_vec.sparseVector.indices,
                sparseValues=q_vec.sparseVector.values,
                permissionScope=authz_out.permissionScope,
                candidatePoolSize=20,
                correlationId=request_id
            )
        )
        s3_dur = (time.perf_counter() - s3_start) * 1000.0
        if not retrieve_res.is_ok:
            return Err(retrieve_res.error)
        retrieved_candidates = retrieve_res.value.candidates
        stages.append(PipelineStageMetricsDTO(stageName="retrieve", durationMs=s3_dur, status="OK"))

        # 4. Rerank
        s4_start = time.perf_counter()
        rerank_res = await self.rerank_service.rerank_candidates(
            RerankRequestDTO(
                tenantId=tenant_id,
                query=authz_out.rewrittenQuery,
                candidates=retrieved_candidates,
                topK=5,
                correlationId=request_id
            )
        )
        s4_dur = (time.perf_counter() - s4_start) * 1000.0
        if not rerank_res.is_ok:
            return Err(rerank_res.error)
        top_chunks = rerank_res.value.rankedChunks
        stages.append(PipelineStageMetricsDTO(stageName="rerank", durationMs=s4_dur, status="OK"))

        # 5. Security Inspection on Context & Query
        s_sec_start = time.perf_counter()
        sec_query_res = await self.security_service.inspect_content(
            SecurityInspectionRequestDTO(
                tenantId=tenant_id,
                content=authz_out.rewrittenQuery,
                sourceType="USER_QUERY",
                correlationId=request_id
            )
        )
        s_sec_dur = (time.perf_counter() - s_sec_start) * 1000.0
        stages.append(PipelineStageMetricsDTO(stageName="security", durationMs=s_sec_dur, status="OK"))
        safe_query = sec_query_res.value.sanitizedContent if sec_query_res.is_ok else authz_out.rewrittenQuery

        # 6. Generate
        s5_start = time.perf_counter()
        gen_res = await self.generate_service.generate_answer(
            GenerationRequestDTO(
                tenantId=tenant_id,
                query=safe_query,
                contextChunks=top_chunks,
                correlationId=request_id
            )
        )
        s5_dur = (time.perf_counter() - s5_start) * 1000.0
        if not gen_res.is_ok:
            return Err(gen_res.error)
        gen_out = gen_res.value
        stages.append(PipelineStageMetricsDTO(stageName="generate", durationMs=s5_dur, status="OK"))

        # 7. Output Guard
        s6_start = time.perf_counter()
        guard_res = await self.guard_service.inspect_and_sanitize(
            GuardInspectionRequestDTO(
                tenantId=tenant_id,
                query=authz_out.rewrittenQuery,
                rawAnswer=gen_out.answer,
                providedChunkIds=[c.chunkId for c in top_chunks],
                stripLinks=True,
                correlationId=request_id
            )
        )
        s6_dur = (time.perf_counter() - s6_start) * 1000.0
        if not guard_res.is_ok:
            return Err(guard_res.error)
        guard_out = guard_res.value
        stages.append(PipelineStageMetricsDTO(stageName="output_guard", durationMs=s6_dur, status="OK"))

        total_dur = (time.perf_counter() - t0) * 1000.0

        # Record Telemetry
        await self.obs_service.record_pipeline_telemetry(
            RequestTelemetryEnvelopeDTO(
                requestId=request_id,
                tenantId=tenant_id,
                userId=user_id,
                traceId=trace_id,
                stages=tuple(stages),
                totalDurationMs=total_dur,
                rewrittenQuery=authz_out.rewrittenQuery,
                retrievedChunkCount=len(retrieved_candidates),
                rerankedChunkCount=len(top_chunks),
                promptTokens=gen_out.inputTokens,
                generatedTokens=gen_out.outputTokens,
                hasError=False,
                timestamp=utc_now_iso(),
                correlationId=request_id
            )
        )

        return Ok({
            "requestId": request_id,
            "tenantId": tenant_id,
            "query": query,
            "rewrittenQuery": authz_out.rewrittenQuery,
            "answer": guard_out.sanitizedAnswer,
            "citedChunkIds": list(guard_out.validCitationIds),
            "abstained": gen_out.abstained,
            "isGrounded": guard_out.isGrounded,
            "totalDurationMs": round(total_dur, 2)
        })
