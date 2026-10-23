from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.authz_rewrite.contracts.authz_rewrite_types import (
    RewriteInputDTO,
    RewrittenQueryOutputDTO,
    ConversationTurn,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[RewriteInputDTO, ValidationError]:
    try:
        dto = RewriteInputDTO.model_validate(payload)
        if not dto.query.strip():
            return Err(ValidationError("query must be a non-empty string"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid payload format: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid payload format: {str(err)}"))


def map_output_to_api(dto: RewrittenQueryOutputDTO) -> Dict[str, Any]:
    return {
        "originalQuery": dto.originalQuery,
        "rewrittenQuery": dto.rewrittenQuery,
        "wasRewritten": dto.wasRewritten,
        "permissionScope": {
            "tenantId": dto.permissionScope.tenantId,
            "userId": dto.permissionScope.userId,
            "allowedAcls": list(dto.permissionScope.allowedAcls),
            "allowedPartitions": list(dto.permissionScope.allowedPartitions)
        },
        "resolvedTenantId": dto.resolvedTenantId
    }
