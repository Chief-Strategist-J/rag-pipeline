import time
from typing import List, Tuple
from src.features.rerank.contracts.rerank_types import (
    RerankRequestDTO,
    RerankResultDTO,
    RerankedChunkDTO,
)
from src.features.rerank.infrastructure.ports.rerank_ports import CrossEncoderModelPort
from src.features.rerank.domain.machines.rerank_machine import (
    RerankState,
    RerankEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class RerankWorkflow:
    def __init__(self, model_port: CrossEncoderModelPort) -> None:
        self._model = model_port

    async def execute(
        self,
        request: RerankRequestDTO
    ) -> Result[RerankResultDTO, ApplicationError]:
        start_time = time.perf_counter()
        state = RerankState.INITIALIZED

        t_prep = transition_state(state, RerankEvent.PREPARE)
        if not t_prep.is_ok:
            return Err(t_prep.error)
        state = t_prep.value

        candidates = request.candidates
        if not candidates:
            return Ok(
                RerankResultDTO(
                    tenantId=request.tenantId,
                    query=request.query,
                    totalEvaluated=0,
                    selectedCount=0,
                    rankedChunks=(),
                    latencyMs=0.0,
                    correlationId=request.correlationId
                )
            )

        texts = [c.content for c in candidates]

        t_score = transition_state(state, RerankEvent.SCORE)
        if not t_score.is_ok:
            return Err(t_score.error)
        state = t_score.value

        score_res = await self._model.compute_similarity_scores(query=request.query, texts=texts)
        if not score_res.is_ok:
            return Err(score_res.error)
        scores = score_res.value

        t_rank = transition_state(state, RerankEvent.RANK)
        if not t_rank.is_ok:
            return Err(t_rank.error)
        state = t_rank.value

        paired: List[Tuple[float, int, any]] = []
        for idx, (chunk, score) in enumerate(zip(candidates, scores)):
            if score >= request.minScoreThreshold:
                paired.append((score, idx + 1, chunk))

        paired.sort(key=lambda x: x[0], reverse=True)
        top_selected = paired[:request.topK]

        ranked_chunks: List[RerankedChunkDTO] = []
        for new_rank, (score, orig_rank, chunk) in enumerate(top_selected, start=1):
            ranked_chunks.append(
                RerankedChunkDTO(
                    chunkId=chunk.chunkId,
                    documentId=chunk.documentId,
                    tenantId=chunk.tenantId,
                    version=chunk.version,
                    sectionTitle=chunk.sectionTitle,
                    content=chunk.content,
                    relevanceScore=score,
                    originalRank=orig_rank,
                    rerankedRank=new_rank,
                    metadata=chunk.metadata
                )
            )

        t_comp = transition_state(state, RerankEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return Ok(
            RerankResultDTO(
                tenantId=request.tenantId,
                query=request.query,
                totalEvaluated=len(candidates),
                selectedCount=len(ranked_chunks),
                rankedChunks=tuple(ranked_chunks),
                latencyMs=duration_ms,
                correlationId=request.correlationId
            )
        )
