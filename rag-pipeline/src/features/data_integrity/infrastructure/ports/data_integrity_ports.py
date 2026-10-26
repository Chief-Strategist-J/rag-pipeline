from typing import Protocol, Sequence, Tuple
from src.features.data_integrity.contracts.data_integrity_types import (
    EntityPayloadDTO,
    IntegrityViolationDTO,
)
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class DataIntegrityRepositoryPort(Protocol):
    async def verify_storage_constraints(
        self,
        entity: EntityPayloadDTO
    ) -> Result[bool, Tuple[IntegrityViolationDTO, ...]]:
        ...

    async def execute_violation_count_check(
        self,
        rule_name: str
    ) -> Result[int, ApplicationError]:
        ...
