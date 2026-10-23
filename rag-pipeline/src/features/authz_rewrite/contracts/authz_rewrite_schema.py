from typing import Dict, Any
from src.features.authz_rewrite.contracts.authz_rewrite_types import (
    RewriteInputDTO,
    RewrittenQueryOutputDTO,
    ConversationTurn,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[RewriteInputDTO, ValidationError]:
    try:
        query = payload.get("query")
        if not query or not isinstance(query, str) or not query.strip():
            return Err(ValidationError("query must be a non-empty string"))

        tenant_id = payload.get("tenantId")
        if not tenant_id or not isinstance(tenant_id, str):
            return Err(ValidationError("tenantId must be a valid string"))

        user_id = payload.get("userId")
        if not user_id or not isinstance(user_id, str):
            return Err(ValidationError("userId must be a valid string"))

        raw_history = payload.get("conversationHistory", [])
        history = tuple(
            ConversationTurn(
                role=str(turn.get("role", "user")),
                content=str(turn.get("content", ""))
            )
            for turn in raw_history
            if isinstance(turn, dict)
        )

        return Ok(
            RewriteInputDTO(
                query=query.strip(),
                tenantId=tenant_id,
                userId=user_id,
                conversationHistory=history,
                skipRewriteIfFirstTurn=bool(payload.get("skipRewriteIfFirstTurn", True))
            )
        )
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
