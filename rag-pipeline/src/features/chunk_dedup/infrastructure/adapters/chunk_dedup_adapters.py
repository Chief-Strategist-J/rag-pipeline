from typing import Optional, Dict
from src.features.chunk_dedup.infrastructure.ports.chunk_dedup_ports import FingerprintStoragePort
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class MemoryFingerprintStorageAdapter(FingerprintStoragePort):
    def __init__(self) -> None:
        self.fingerprints: Dict[str, int] = {}

    async def get_existing_version_by_hash(
        self,
        tenant_id: str,
        content_hash: str
    ) -> Result[Optional[int], ApplicationError]:
        key = f"{tenant_id}:{content_hash}"
        return Ok(self.fingerprints.get(key))

    async def register_content_hash(
        self,
        tenant_id: str,
        document_id: str,
        version: int,
        content_hash: str
    ) -> Result[bool, ApplicationError]:
        key = f"{tenant_id}:{content_hash}"
        self.fingerprints[key] = max(self.fingerprints.get(key, 0), version)
        return Ok(True)
