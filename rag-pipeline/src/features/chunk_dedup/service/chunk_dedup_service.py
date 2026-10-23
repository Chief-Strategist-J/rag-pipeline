from typing import Protocol
from src.features.chunk_dedup.contracts.chunk_dedup_types import (
    ChunkingRequestDTO,
    ChunkingResultDTO,
)
from src.features.chunk_dedup.infrastructure.ports.chunk_dedup_ports import FingerprintStoragePort
from src.features.chunk_dedup.domain.workflows.chunk_dedup_workflow import ChunkDedupWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class ChunkDedupServiceDeps(Protocol):
    fingerprint_port: FingerprintStoragePort


class ChunkDedupService:
    def __init__(self, deps: ChunkDedupServiceDeps) -> None:
        self._workflow = ChunkDedupWorkflow(fingerprint_port=deps.fingerprint_port)

    async def process_chunks(
        self,
        request: ChunkingRequestDTO
    ) -> Result[ChunkingResultDTO, ApplicationError]:
        try:
            return await self._workflow.execute(request)
        except Exception as err:
            return Err(ApplicationError(str(err), code="CHUNK_DEDUP_SERVICE_ERROR", status_code=500))
