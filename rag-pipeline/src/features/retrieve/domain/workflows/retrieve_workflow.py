from typing import Dict, List
from src.features.retrieve.contracts.retrieve_types import (
    RetrieveRequestDTO,
    RetrieveResultDTO,
    ScoredChunkDTO,
)
from src.features.retrieve.infrastructure.ports.retrieve_ports import HybridVectorSearchPort
from src.features.retrieve.domain.rules.retrieve_rules import fuse_ranks_rrf
from src.features.retrieve.domain.machines.retrieve_machine import (
    RetrieveState,
    RetrieveEvent,
    transition_state,
)
from src.features.embed_enrich.contracts.embed_enrich_types import EnrichedChunkVectorDTO
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class RetrieveWorkflow:
    def __init__(self, search_port: HybridVectorSearchPort) -> None:
        self._search = search_port

    async def execute(
        self,
        request: RetrieveRequestDTO
    ) -> Result[RetrieveResultDTO, ApplicationError]:
        state = RetrieveState.INITIALIZED

        t_res = transition_state(state, RetrieveEvent.RESOLVE_FILTERS)
        if not t_res.is_ok:
            return Err(t_res.error)
        state = t_res.value

        t_sea = transition_state(state, RetrieveEvent.SEARCH_HYBRID)
        if not t_sea.is_ok:
            return Err(t_sea.error)
        state = t_sea.value

        dense_res = await self._search.search_dense(
            tenant_id=request.tenantId,
            vector=request.denseVector,
            permission_scope=request.permissionScope,
            limit=request.candidatePoolSize
        )
        if not dense_res.is_ok:
            return Err(dense_res.error)

        sparse_res = await self._search.search_sparse(
            tenant_id=request.tenantId,
            indices=request.sparseIndices,
            values=request.sparseValues,
            permission_scope=request.permissionScope,
            limit=request.candidatePoolSize
        )
        if not sparse_res.is_ok:
            return Err(sparse_res.error)

        dense_chunks = dense_res.value
        sparse_chunks = sparse_res.value

        chunk_by_id: Dict[str, EnrichedChunkVectorDTO] = {}
        for c in dense_chunks:
            chunk_by_id[c.chunkId] = c
        for c in sparse_chunks:
            chunk_by_id[c.chunkId] = c

        dense_ids = [c.chunkId for c in dense_chunks]
        sparse_ids = [c.chunkId for c in sparse_chunks]

        t_fuse = transition_state(state, RetrieveEvent.FUSE_RRF)
        if not t_fuse.is_ok:
            return Err(t_fuse.error)
        state = t_fuse.value

        fused = fuse_ranks_rrf(dense_ids, sparse_ids, k=60)
        scored_candidates: List[ScoredChunkDTO] = []

        for chunk_id, rrf_score, dense_rank, sparse_rank in fused:
            chunk = chunk_by_id.get(chunk_id)
            if not chunk:
                continue
            scored_candidates.append(
                ScoredChunkDTO(
                    chunkId=chunk.chunkId,
                    documentId=chunk.documentId,
                    tenantId=chunk.tenantId,
                    version=chunk.version,
                    sectionTitle=chunk.sectionTitle,
                    content=chunk.content,
                    rrfScore=rrf_score,
                    denseRank=dense_rank,
                    sparseRank=sparse_rank,
                    metadata=chunk.metadata
                )
            )

        t_comp = transition_state(state, RetrieveEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(
            RetrieveResultDTO(
                tenantId=request.tenantId,
                query=request.query,
                totalRetrieved=len(scored_candidates),
                candidates=tuple(scored_candidates),
                correlationId=request.correlationId
            )
        )
