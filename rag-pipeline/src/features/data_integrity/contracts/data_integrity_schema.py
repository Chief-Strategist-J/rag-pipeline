from typing import Dict, Any, Tuple
from pydantic import ValidationError as PydanticValidationError
from src.features.data_integrity.contracts.data_integrity_types import (
    EntityPayloadDTO,
    IntegrityValidationRequestDTO,
    IntegrityValidationResultDTO,
    IntegrityViolationDTO,
    GateLevel,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def normalize_and_parse_entity(
    raw: Dict[str, Any]
) -> Result[EntityPayloadDTO, Tuple[IntegrityViolationDTO, ...]]:
    violations = []
    
    source = raw.get("source")
    if not isinstance(source, str) or not source.strip():
        violations.append(
            IntegrityViolationDTO(
                gate=GateLevel.INGRESS,
                field="source",
                ruleName="orders_source_nn_ck",
                message="Source is required and must not be empty.",
                rejectedValue=str(source)
            )
        )

    ext_id = raw.get("externalId")
    if not isinstance(ext_id, str) or not ext_id.strip():
        violations.append(
            IntegrityViolationDTO(
                gate=GateLevel.INGRESS,
                field="externalId",
                ruleName="orders_external_id_len_ck",
                message="External ID must be 1 to 64 non-empty trimmed characters.",
                rejectedValue=str(ext_id)
            )
        )
    elif len(ext_id.strip()) > 64:
        violations.append(
            IntegrityViolationDTO(
                gate=GateLevel.INGRESS,
                field="externalId",
                ruleName="orders_external_id_len_ck",
                message="External ID must not exceed 64 characters.",
                rejectedValue=ext_id
            )
        )

    currency = raw.get("currency")
    if not isinstance(currency, str) or len(currency.strip()) != 3:
        violations.append(
            IntegrityViolationDTO(
                gate=GateLevel.INGRESS,
                field="currency",
                ruleName="orders_currency_format_ck",
                message="Currency must be exactly 3 alphabetic characters (ISO 4217).",
                rejectedValue=str(currency)
            )
        )

    amount = raw.get("amount")
    if not isinstance(amount, (int, float)):
        violations.append(
            IntegrityViolationDTO(
                gate=GateLevel.INGRESS,
                field="amount",
                ruleName="orders_amount_type_ck",
                message="Amount must be a numeric value.",
                rejectedValue=str(amount)
            )
        )

    if violations:
        return Err(tuple(violations))

    normalized_data = dict(raw)
    normalized_data["externalId"] = ext_id.strip()
    normalized_data["currency"] = currency.strip().upper()

    try:
        dto = EntityPayloadDTO.model_validate(normalized_data)
        return Ok(dto)
    except PydanticValidationError as pve:
        pve_violations = [
            IntegrityViolationDTO(
                gate=GateLevel.INGRESS,
                field=".".join(str(loc) for loc in err["loc"]),
                ruleName="schema_validation_error",
                message=err["msg"],
                rejectedValue=None
            )
            for err in pve.errors()
        ]
        return Err(tuple(pve_violations))


def map_input_from_api(
    payload: Dict[str, Any]
) -> Result[IntegrityValidationRequestDTO, ValidationError]:
    try:
        dto = IntegrityValidationRequestDTO.model_validate(payload)
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid integrity validation request: {str(err)}"))


def map_output_to_api(
    dto: IntegrityValidationResultDTO
) -> Dict[str, Any]:
    return {
        "tenantId": dto.tenantId,
        "correlationId": dto.correlationId,
        "isValid": dto.isValid,
        "normalizedEntity": dto.normalizedEntity.model_dump() if dto.normalizedEntity else None,
        "violations": [v.model_dump() for v in dto.violations],
    }
