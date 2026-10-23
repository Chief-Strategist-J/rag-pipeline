from src.features.security.contracts.security_types import (
    SecurityInspectionRequestDTO,
    SecurityInspectionResultDTO,
)
from src.features.security.infrastructure.ports.security_ports import ThreatDetectionPort
from src.features.security.domain.rules.security_rules import (
    detect_prompt_injections,
    neutralize_injections,
)
from src.features.security.domain.machines.security_machine import (
    SecurityState,
    SecurityEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class SecurityWorkflow:
    def __init__(self, threat_port: ThreatDetectionPort) -> None:
        self._threat_port = threat_port

    async def execute(
        self,
        request: SecurityInspectionRequestDTO
    ) -> Result[SecurityInspectionResultDTO, ApplicationError]:
        state = SecurityState.INITIALIZED

        t_scan = transition_state(state, SecurityEvent.SCAN)
        if not t_scan.is_ok:
            return Err(t_scan.error)
        state = t_scan.value

        threats = detect_prompt_injections(request.content)
        is_safe = len(threats) == 0

        t_neut = transition_state(state, SecurityEvent.NEUTRALIZE)
        if not t_neut.is_ok:
            return Err(t_neut.error)
        state = t_neut.value

        sanitized_content = request.content
        if not is_safe:
            sanitized_content = neutralize_injections(request.content, threats)
            log_res = await self._threat_port.log_detected_threats(
                tenant_id=request.tenantId,
                correlation_id=request.correlationId,
                threats=threats
            )
            if not log_res.is_ok:
                return Err(log_res.error)

        t_comp = transition_state(state, SecurityEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(
            SecurityInspectionResultDTO(
                tenantId=request.tenantId,
                isSafe=is_safe,
                sanitizedContent=sanitized_content,
                threats=tuple(threats),
                threatCount=len(threats),
                correlationId=request.correlationId
            )
        )
