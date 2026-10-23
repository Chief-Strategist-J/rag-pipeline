from typing import Protocol
from src.features.observability.contracts.observability_types import RequestTelemetryEnvelopeDTO
from src.features.observability.infrastructure.ports.observability_ports import TelemetrySpanCollectorPort
from src.features.observability.domain.workflows.observability_workflow import ObservabilityWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class ObservabilityServiceDeps(Protocol):
    collector_port: TelemetrySpanCollectorPort


class ObservabilityService:
    def __init__(self, deps: ObservabilityServiceDeps) -> None:
        self._workflow = ObservabilityWorkflow(collector_port=deps.collector_port)

    async def record_pipeline_telemetry(
        self,
        envelope: RequestTelemetryEnvelopeDTO
    ) -> Result[RequestTelemetryEnvelopeDTO, ApplicationError]:
        try:
            return await self._workflow.execute(envelope)
        except Exception as err:
            return Err(ApplicationError(str(err), code="OBSERVABILITY_SERVICE_ERROR", status_code=500))
