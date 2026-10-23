from typing import Protocol
from src.features.observability.contracts.observability_types import RequestTelemetryEnvelopeDTO
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class TelemetrySpanCollectorPort(Protocol):
    async def export_telemetry_envelope(
        self,
        envelope: RequestTelemetryEnvelopeDTO
    ) -> Result[bool, ApplicationError]:
        ...
