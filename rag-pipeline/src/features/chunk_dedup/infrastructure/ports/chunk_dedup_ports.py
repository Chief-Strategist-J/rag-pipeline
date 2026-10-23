from typing import Protocol, Optional
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class FingerprintStoragePort(Protocol):
    async def get_existing_version_by_hash(
        self,
        tenant_id: str,
        content_hash: str
    ) -> Result[Optional[int], ApplicationError]:
        ...

    async def register_content_hash(
        self,
        tenant_id: str,
        document_id: str,
        version: int,
        content_hash: str
    ) -> Result[bool, ApplicationError]:
        ...
