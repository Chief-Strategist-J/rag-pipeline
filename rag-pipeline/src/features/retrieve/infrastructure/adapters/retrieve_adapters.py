from typing import Sequence, List
from src.features.retrieve.infrastructure.ports.retrieve_ports import HybridVectorSearchPort
from src.features.authz_rewrite.contracts.authz_rewrite_types import PermissionScope
from src.features.embed_enrich.contracts.embed_enrich_types import EnrichedChunkVectorDTO
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class MemoryHybridVectorSearchAdapter(HybridVectorSearchPort):
    def __init__(self, seeded_points: Sequence[EnrichedChunkVectorDTO] = ()) -> None:
        self._points = list(seeded_points)

    def add_point(self, point: EnrichedChunkVectorDTO) -> None:
        self._points.append(point)

    async def search_dense(
        self,
        tenant_id: str,
        vector: Sequence[float],
        permission_scope: PermissionScope,
        limit: int
    ) -> Result[Sequence[EnrichedChunkVectorDTO], ApplicationError]:
        filtered = [
            p for p in self._points
            if p.tenantId == tenant_id and any(acl in permission_scope.allowedAcls for acl in p.aclTags)
        ]
        return Ok(tuple(filtered[:limit]))

    async def search_sparse(
        self,
        tenant_id: str,
        indices: Sequence[int],
        values: Sequence[float],
        permission_scope: PermissionScope,
        limit: int
    ) -> Result[Sequence[EnrichedChunkVectorDTO], ApplicationError]:
        filtered = [
            p for p in self._points
            if p.tenantId == tenant_id and any(acl in permission_scope.allowedAcls for acl in p.aclTags)
        ]
        return Ok(tuple(filtered[:limit]))
