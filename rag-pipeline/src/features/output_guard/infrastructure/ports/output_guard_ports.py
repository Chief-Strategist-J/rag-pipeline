from typing import Protocol, Sequence
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class GuardAuditPort(Protocol):
    async def record_guard_event(
        self,
        tenant_id: str,
        correlation_id: str,
        action: str,
        hallucinated_citations: Sequence[str],
        removed_links_count: int
    ) -> Result[bool, ApplicationError]:
        ...
