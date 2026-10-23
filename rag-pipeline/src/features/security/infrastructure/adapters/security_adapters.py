from typing import Sequence, List, Dict
from src.features.security.infrastructure.ports.security_ports import ThreatDetectionPort
from src.features.security.contracts.security_types import DetectedThreatDTO
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class MemoryThreatDetectionAdapter(ThreatDetectionPort):
    def __init__(self) -> None:
        self.recorded_threats: List[Dict[str, any]] = []

    async def log_detected_threats(
        self,
        tenant_id: str,
        correlation_id: str,
        threats: Sequence[DetectedThreatDTO]
    ) -> Result[bool, ApplicationError]:
        self.recorded_threats.append({
            "tenant_id": tenant_id,
            "correlation_id": correlation_id,
            "threats": list(threats)
        })
        return Ok(True)
