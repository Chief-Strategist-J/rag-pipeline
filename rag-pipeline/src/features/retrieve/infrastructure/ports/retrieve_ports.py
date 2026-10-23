from typing import Protocol, Sequence, Tuple, Dict
from src.features.authz_rewrite.contracts.authz_rewrite_types import PermissionScope
from src.features.embed_enrich.contracts.embed_enrich_types import EnrichedChunkVectorDTO
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class HybridVectorSearchPort(Protocol):
    async def search_dense(
        self,
        tenant_id: str,
        vector: Sequence[float],
        permission_scope: PermissionScope,
        limit: int
    ) -> Result[Sequence[EnrichedChunkVectorDTO], ApplicationError]:
        ...

    async def search_sparse(
        self,
        tenant_id: str,
        indices: Sequence[int],
        values: Sequence[float],
        permission_scope: PermissionScope,
        limit: int
    ) -> Result[Sequence[EnrichedChunkVectorDTO], ApplicationError]:
        ...
