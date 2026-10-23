from typing import List
from src.features.chunk_dedup.contracts.chunk_dedup_types import (
    ChunkingRequestDTO,
    ChunkingResultDTO,
    ChunkDTO,
)
from src.features.chunk_dedup.infrastructure.ports.chunk_dedup_ports import FingerprintStoragePort
from src.features.chunk_dedup.domain.rules.chunk_dedup_rules import (
    generate_deterministic_chunk_id,
    compute_content_hash,
    estimate_token_count,
)
from src.features.chunk_dedup.domain.machines.chunk_dedup_machine import (
    ChunkDedupState,
    ChunkDedupEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class ChunkDedupWorkflow:
    def __init__(self, fingerprint_port: FingerprintStoragePort) -> None:
        self._fingerprints = fingerprint_port

    async def execute(
        self,
        request: ChunkingRequestDTO
    ) -> Result[ChunkingResultDTO, ApplicationError]:
        state = ChunkDedupState.INITIALIZED

        t_agg = transition_state(state, ChunkDedupEvent.AGGREGATE)
        if not t_agg.is_ok:
            return Err(t_agg.error)
        state = t_agg.value

        raw_chunks: List[ChunkDTO] = []
        current_section = "General"
        offset = 0

        for block in request.blocks:
            if block.sectionTitle:
                current_section = block.sectionTitle

            chunk_id = generate_deterministic_chunk_id(
                document_id=request.documentId,
                version=request.version,
                offset_index=offset
            )
            content_hash = compute_content_hash(block.content)
            token_count = estimate_token_count(block.content)

            chunk = ChunkDTO(
                chunkId=chunk_id,
                documentId=request.documentId,
                tenantId=request.tenantId,
                version=request.version,
                offsetIndex=offset,
                sectionTitle=current_section,
                content=block.content,
                tokenCount=token_count,
                contentHash=content_hash,
                isCurrent=True,
                metadata={"source_block_id": block.blockId}
            )
            raw_chunks.append(chunk)
            offset += 1

        t_chk = transition_state(state, ChunkDedupEvent.CHUNK)
        if not t_chk.is_ok:
            return Err(t_chk.error)
        state = t_chk.value

        t_ded = transition_state(state, ChunkDedupEvent.DEDUPLICATE)
        if not t_ded.is_ok:
            return Err(t_ded.error)
        state = t_ded.value

        deduplicated_count = 0
        final_chunks: List[ChunkDTO] = []

        for chunk in raw_chunks:
            existing_ver_res = await self._fingerprints.get_existing_version_by_hash(
                tenant_id=request.tenantId,
                content_hash=chunk.contentHash
            )
            if not existing_ver_res.is_ok:
                return Err(existing_ver_res.error)

            existing_ver = existing_ver_res.value
            if existing_ver is not None and existing_ver > request.version:
                deduplicated_count += 1
                final_chunks.append(chunk.model_copy(update={"isCurrent": False}))
            else:
                await self._fingerprints.register_content_hash(
                    tenant_id=request.tenantId,
                    document_id=request.documentId,
                    version=request.version,
                    content_hash=chunk.contentHash
                )
                final_chunks.append(chunk)

        t_comp = transition_state(state, ChunkDedupEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(
            ChunkingResultDTO(
                documentId=request.documentId,
                tenantId=request.tenantId,
                version=request.version,
                totalChunks=len(final_chunks),
                deduplicatedCount=deduplicated_count,
                chunks=final_chunks,
                correlationId=request.correlationId
            )
        )
