from typing import Protocol, Sequence
from src.features.security.contracts.security_types import DetectedThreatDTO
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class ThreatDetectionPort(Protocol):
    async def log_detected_threats(
        self,
        tenant_id: str,
        correlation_id: str,
        threats: Sequence[DetectedThreatDTO]
    ) -> Result[bool, ApplicationError]:
        ...
