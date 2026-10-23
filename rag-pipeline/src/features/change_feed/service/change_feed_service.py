from typing import Protocol
from src.features.change_feed.contracts.change_feed_types import (
    DocumentChangeEventDTO,
    ChangeProcessingResultDTO,
)
from src.features.change_feed.infrastructure.ports.change_feed_ports import (
    ChangeFeedRepositoryPort,
    DownstreamInvalidationPort,
)
from src.features.change_feed.domain.workflows.change_feed_workflow import ChangeFeedWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class ChangeFeedServiceDeps(Protocol):
    repository_port: ChangeFeedRepositoryPort
    invalidation_port: DownstreamInvalidationPort


class ChangeFeedService:
    def __init__(self, deps: ChangeFeedServiceDeps) -> None:
        self._workflow = ChangeFeedWorkflow(
            repository_port=deps.repository_port,
            invalidation_port=deps.invalidation_port
        )

    async def process_change_event(
        self,
        event: DocumentChangeEventDTO
    ) -> Result[ChangeProcessingResultDTO, ApplicationError]:
        try:
            return await self._workflow.execute(event)
        except Exception as err:
            return Err(ApplicationError(str(err), code="CHANGE_FEED_SERVICE_ERROR", status_code=500))
