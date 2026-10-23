from typing import Protocol
from src.features.index.contracts.index_types import (
    IndexUpsertRequestDTO,
    IndexUpsertResultDTO,
)
from src.features.index.infrastructure.ports.index_ports import (
    QdrantCollectionPort,
    IndexMetadataRegistryPort,
)
from src.features.index.domain.workflows.index_workflow import IndexWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class IndexServiceDeps(Protocol):
    qdrant_port: QdrantCollectionPort
    registry_port: IndexMetadataRegistryPort


class IndexService:
    def __init__(self, deps: IndexServiceDeps) -> None:
        self._workflow = IndexWorkflow(
            qdrant_port=deps.qdrant_port,
            registry_port=deps.registry_port
        )

    async def upsert_vectors(
        self,
        request: IndexUpsertRequestDTO
    ) -> Result[IndexUpsertResultDTO, ApplicationError]:
        try:
            return await self._workflow.execute(request)
        except Exception as err:
            return Err(ApplicationError(str(err), code="INDEX_SERVICE_ERROR", status_code=500))
