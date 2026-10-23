from typing import List
from src.features.embed_enrich.contracts.embed_enrich_types import (
    EmbeddingRequestDTO,
    EmbeddingResultDTO,
    EnrichedChunkVectorDTO,
    SparseVectorDTO,
)
from src.features.embed_enrich.infrastructure.ports.embed_enrich_ports import (
    VectorEmbeddingModelPort,
    SparseEncodingPort,
)
from src.features.embed_enrich.domain.machines.embed_enrich_machine import (
    EmbedEnrichState,
    EmbedEnrichEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError
from src.shared.utils.time_utils import utc_now_iso


class EmbedEnrichWorkflow:
    def __init__(
        self,
        dense_port: VectorEmbeddingModelPort,
        sparse_port: SparseEncodingPort
    ) -> None:
        self._dense = dense_port
        self._sparse = sparse_port

    async def execute(
        self,
        request: EmbeddingRequestDTO
    ) -> Result[EmbeddingResultDTO, ApplicationError]:
        state = EmbedEnrichState.INITIALIZED

        t_dense = transition_state(state, EmbedEnrichEvent.EMBED_DENSE)
        if not t_dense.is_ok:
            return Err(t_dense.error)
        state = t_dense.value

        texts = [c.get("content", "") for c in request.chunks]
        dense_res = await self._dense.generate_dense_embeddings(texts)
        if not dense_res.is_ok:
            return Err(dense_res.error)
        dense_vectors = dense_res.value

        t_sparse = transition_state(state, EmbedEnrichEvent.ENCODE_SPARSE)
        if not t_sparse.is_ok:
            return Err(t_sparse.error)
        state = t_sparse.value

        sparse_res = await self._sparse.generate_sparse_vectors(texts)
        if not sparse_res.is_ok:
            return Err(sparse_res.error)
        sparse_vectors = sparse_res.value

        t_meta = transition_state(state, EmbedEnrichEvent.ATTACH_METADATA)
        if not t_meta.is_ok:
            return Err(t_meta.error)
        state = t_meta.value

        enriched_vectors: List[EnrichedChunkVectorDTO] = []
        now_ts = utc_now_iso()

        for idx, chunk_map in enumerate(request.chunks):
            indices, values = sparse_vectors[idx]
            vec_dto = EnrichedChunkVectorDTO(
                chunkId=chunk_map.get("chunkId", f"{request.documentId}:c{idx:04d}"),
                documentId=request.documentId,
                tenantId=request.tenantId,
                version=request.version,
                sectionTitle=chunk_map.get("sectionTitle", "General"),
                content=chunk_map.get("content", ""),
                denseVector=dense_vectors[idx],
                sparseVector=SparseVectorDTO(indices=indices, values=values),
                aclTags=tuple(request.aclTags) if request.aclTags else ("INTERNAL", "PUBLIC"),
                metadata=chunk_map,
                createdAt=now_ts
            )
            enriched_vectors.append(vec_dto)

        t_comp = transition_state(state, EmbedEnrichEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(
            EmbeddingResultDTO(
                tenantId=request.tenantId,
                documentId=request.documentId,
                version=request.version,
                totalVectors=len(enriched_vectors),
                vectors=tuple(enriched_vectors),
                correlationId=request.correlationId
            )
        )
