from typing import List, Sequence, Tuple
import re
from src.features.data_integrity.contracts.data_integrity_types import (
    EntityPayloadDTO,
    IntegrityViolationDTO,
    GateLevel,
)

VALID_STATUSES = {"draft", "confirmed", "shipped", "cancelled", "returned"}
CURRENCY_REGEX = re.compile(r"^[A-Z]{3}$")


def evaluate_domain_invariants(
    entity: EntityPayloadDTO
) -> Tuple[IntegrityViolationDTO, ...]:
    violations: List[IntegrityViolationDTO] = []

    if entity.amount < 0.0:
        violations.append(
            IntegrityViolationDTO(
                gate=GateLevel.DOMAIN,
                field="amount",
                ruleName="orders_amount_nonneg_ck",
                message="Amount must be greater than or equal to 0.00.",
                rejectedValue=str(entity.amount)
            )
        )

    if not CURRENCY_REGEX.match(entity.currency):
        violations.append(
            IntegrityViolationDTO(
                gate=GateLevel.DOMAIN,
                field="currency",
                ruleName="orders_currency_iso_ck",
                message="Currency must match ISO 3-letter uppercase standard.",
                rejectedValue=entity.currency
            )
        )

    if entity.status not in VALID_STATUSES:
        violations.append(
            IntegrityViolationDTO(
                gate=GateLevel.DOMAIN,
                field="status",
                ruleName="orders_status_fk",
                message=f"Status '{entity.status}' is not recognized in allowed state table.",
                rejectedValue=entity.status
            )
        )

    is_shipped = (entity.status == "shipped")
    has_shipped_at = bool(entity.shippedAt and entity.shippedAt.strip())
    if is_shipped != has_shipped_at:
        violations.append(
            IntegrityViolationDTO(
                gate=GateLevel.DOMAIN,
                field="shippedAt",
                ruleName="orders_shipped_at_status_agreement_ck",
                message="Shipped orders must have shippedAt, and shippedAt requires status 'shipped'.",
                rejectedValue=str(entity.shippedAt)
            )
        )

    return tuple(violations)
