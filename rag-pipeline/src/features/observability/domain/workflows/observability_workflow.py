from typing import List
from src.features.observability.contracts.observability_types import (
    RequestTelemetryEnvelopeDTO,
    PipelineStageMetricsDTO,
)
from src.features.observability.infrastructure.ports.observability_ports import TelemetrySpanCollectorPort
from src.features.observability.domain.rules.observability_rules import (
    sanitize_sensitive_attributes,
    validate_trace_id_format,
)
from src.features.observability.domain.machines.observability_machine import (
    ObservabilityState,
    ObservabilityEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError, ValidationError


class ObservabilityWorkflow:
    def __init__(self, collector_port: TelemetrySpanCollectorPort) -> None:
        self._collector = collector_port

    async def execute(
        self,
        envelope: RequestTelemetryEnvelopeDTO
    ) -> Result[RequestTelemetryEnvelopeDTO, ApplicationError]:
        state = ObservabilityState.INITIALIZED

        if not validate_trace_id_format(envelope.traceId):
            return Err(ValidationError(f"Invalid W3C trace ID: {envelope.traceId}"))

        t_san = transition_state(state, ObservabilityEvent.SANITIZE)
        if not t_san.is_ok:
            return Err(t_san.error)
        state = t_san.value

        cleaned_stages: List[PipelineStageMetricsDTO] = []
        for stage in envelope.stages:
            cleaned_attrs = sanitize_sensitive_attributes(stage.attributes)
            cleaned_stages.append(stage.model_copy(update={"attributes": cleaned_attrs}))

        clean_envelope = envelope.model_copy(update={"stages": tuple(cleaned_stages)})

        t_rec = transition_state(state, ObservabilityEvent.RECORD)
        if not t_rec.is_ok:
            return Err(t_rec.error)
        state = t_rec.value

        export_res = await self._collector.export_telemetry_envelope(clean_envelope)
        if not export_res.is_ok:
            return Err(export_res.error)

        t_comp = transition_state(state, ObservabilityEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(clean_envelope)
