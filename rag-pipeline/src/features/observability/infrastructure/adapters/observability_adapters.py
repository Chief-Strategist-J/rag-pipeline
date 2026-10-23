from typing import List
from src.features.observability.infrastructure.ports.observability_ports import TelemetrySpanCollectorPort
from src.features.observability.contracts.observability_types import RequestTelemetryEnvelopeDTO
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class MemoryTelemetryCollectorAdapter(TelemetrySpanCollectorPort):
    def __init__(self) -> None:
        self.exported_envelopes: List[RequestTelemetryEnvelopeDTO] = []

    async def export_telemetry_envelope(
        self,
        envelope: RequestTelemetryEnvelopeDTO
    ) -> Result[bool, ApplicationError]:
        self.exported_envelopes.append(envelope)
        return Ok(True)
