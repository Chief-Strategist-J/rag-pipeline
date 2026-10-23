from typing import Protocol
from src.features.embed_enrich.contracts.embed_enrich_types import (
    EmbeddingRequestDTO,
    EmbeddingResultDTO,
)
from src.features.embed_enrich.infrastructure.ports.embed_enrich_ports import (
    VectorEmbeddingModelPort,
    SparseEncodingPort,
)
from src.features.embed_enrich.domain.workflows.embed_enrich_workflow import EmbedEnrichWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class EmbedEnrichServiceDeps(Protocol):
    dense_port: VectorEmbeddingModelPort
    sparse_port: SparseEncodingPort


class EmbedEnrichService:
    def __init__(self, deps: EmbedEnrichServiceDeps) -> None:
        self._workflow = EmbedEnrichWorkflow(
            dense_port=deps.dense_port,
            sparse_port=deps.sparse_port
        )

    async def generate_embeddings(
        self,
        request: EmbeddingRequestDTO
    ) -> Result[EmbeddingResultDTO, ApplicationError]:
        try:
            return await self._workflow.execute(request)
        except Exception as err:
            return Err(ApplicationError(str(err), code="EMBED_ENRICH_SERVICE_ERROR", status_code=500))
