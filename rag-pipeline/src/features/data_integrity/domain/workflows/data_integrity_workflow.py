from typing import List
from src.features.data_integrity.contracts.data_integrity_types import (
    IntegrityValidationRequestDTO,
    IntegrityValidationResultDTO,
    IntegrityViolationDTO,
)
from src.features.data_integrity.contracts.data_integrity_schema import (
    normalize_and_parse_entity,
)
from src.features.data_integrity.domain.rules.data_integrity_rules import (
    evaluate_domain_invariants,
)
from src.features.data_integrity.domain.machines.data_integrity_machine import (
    IntegrityState,
    IntegrityEvent,
    transition_state,
)
from src.features.data_integrity.infrastructure.ports.data_integrity_ports import (
    DataIntegrityRepositoryPort,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class DataIntegrityWorkflow:
    def __init__(self, repo_port: DataIntegrityRepositoryPort) -> None:
        self._repo_port = repo_port

    async def execute(
        self,
        request: IntegrityValidationRequestDTO
    ) -> Result[IntegrityValidationResultDTO, ApplicationError]:
        state = IntegrityState.INITIALIZED
        violations: List[IntegrityViolationDTO] = []

        t1 = transition_state(state, IntegrityEvent.VALIDATE_INGRESS)
        if not t1.is_ok:
            return Err(t1.error)
        state = t1.value

        norm_res = normalize_and_parse_entity(request.payload)
        if not norm_res.is_ok:
            violations.extend(norm_res.error)
            transition_state(state, IntegrityEvent.REJECT)
            return Ok(
                IntegrityValidationResultDTO(
                    tenantId=request.tenantId,
                    correlationId=request.correlationId,
                    isValid=False,
                    normalizedEntity=None,
                    violations=tuple(violations)
                )
            )

        entity = norm_res.value

        t2 = transition_state(state, IntegrityEvent.INSPECT_DOMAIN)
        if not t2.is_ok:
            return Err(t2.error)
        state = t2.value

        domain_violations = evaluate_domain_invariants(entity)
        if domain_violations:
            violations.extend(domain_violations)
            transition_state(state, IntegrityEvent.REJECT)
            return Ok(
                IntegrityValidationResultDTO(
                    tenantId=request.tenantId,
                    correlationId=request.correlationId,
                    isValid=False,
                    normalizedEntity=entity,
                    violations=tuple(violations)
                )
            )

        t3 = transition_state(state, IntegrityEvent.ENFORCE_STORAGE)
        if not t3.is_ok:
            return Err(t3.error)
        state = t3.value

        storage_res = await self._repo_port.verify_storage_constraints(entity)
        if not storage_res.is_ok:
            violations.extend(storage_res.error)
            transition_state(state, IntegrityEvent.REJECT)
            return Ok(
                IntegrityValidationResultDTO(
                    tenantId=request.tenantId,
                    correlationId=request.correlationId,
                    isValid=False,
                    normalizedEntity=entity,
                    violations=tuple(violations)
                )
            )

        t4 = transition_state(state, IntegrityEvent.COMMIT)
        if not t4.is_ok:
            return Err(t4.error)

        return Ok(
            IntegrityValidationResultDTO(
                tenantId=request.tenantId,
                correlationId=request.correlationId,
                isValid=True,
                normalizedEntity=entity,
                violations=()
            )
        )
