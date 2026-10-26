from typing import Tuple, Set
from src.features.data_integrity.infrastructure.ports.data_integrity_ports import (
    DataIntegrityRepositoryPort,
)
from src.features.data_integrity.contracts.data_integrity_types import (
    EntityPayloadDTO,
    IntegrityViolationDTO,
    GateLevel,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError

CONSTRAINT_REGISTRY = {
    "orders_amount_nonneg_ck": "VALIDATION.AMOUNT_NEGATIVE",
    "orders_tenant_ext_uk": "CONFLICT.DUPLICATE_EXTERNAL_ID",
    "orders_status_fk": "VALIDATION.UNKNOWN_STATUS",
    "orders_tenant_fk": "VALIDATION.TENANT_NOT_FOUND",
}


class MemoryDataIntegrityRepositoryAdapter(DataIntegrityRepositoryPort):
    def __init__(self, existing_external_keys: Set[Tuple[str, str, str]] = None) -> None:
        self._keys = existing_external_keys or set()

    async def verify_storage_constraints(
        self,
        entity: EntityPayloadDTO
    ) -> Result[bool, Tuple[IntegrityViolationDTO, ...]]:
        key = (entity.tenantId, entity.source, entity.externalId)
        if key in self._keys:
            violation = IntegrityViolationDTO(
                gate=GateLevel.STORAGE,
                field="externalId",
                ruleName="orders_tenant_ext_uk",
                message="Unique constraint violation: tenant_id, source, and external_id must be unique.",
                rejectedValue=f"{entity.tenantId}:{entity.source}:{entity.externalId}"
            )
            return Err((violation,))
        self._keys.add(key)
        return Ok(True)

    async def execute_violation_count_check(
        self,
        rule_name: str
    ) -> Result[int, ApplicationError]:
        return Ok(0)
