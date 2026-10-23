from typing import Sequence, List, Dict
from src.features.output_guard.infrastructure.ports.output_guard_ports import GuardAuditPort
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class MemoryGuardAuditAdapter(GuardAuditPort):
    def __init__(self) -> None:
        self.audit_records: List[Dict[str, any]] = []

    async def record_guard_event(
        self,
        tenant_id: str,
        correlation_id: str,
        action: str,
        hallucinated_citations: Sequence[str],
        removed_links_count: int
    ) -> Result[bool, ApplicationError]:
        self.audit_records.append({
            "tenant_id": tenant_id,
            "correlation_id": correlation_id,
            "action": action,
            "hallucinated_citations": list(hallucinated_citations),
            "removed_links_count": removed_links_count
        })
        return Ok(True)
