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


class QdrantHybridVectorSearchAdapter(HybridVectorSearchPort):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "rag_corpus_v1",
        fallback_adapter: HybridVectorSearchPort = None
    ) -> None:
        self._host = host
        self._port = port
        self._collection = collection_name
        self._fallback = fallback_adapter or MemoryHybridVectorSearchAdapter()
        self._client = None
        try:
            from qdrant_client import QdrantClient
            self._client = QdrantClient(host=self._host, port=self._port, timeout=3.0)
        except Exception:
            self._client = None

    def add_point(self, point: EnrichedChunkVectorDTO) -> None:
        self._fallback.add_point(point)
        if self._client:
            try:
                from qdrant_client.http import models as qmodels
                collections = [c.name for c in self._client.get_collections().collections]
                if self._collection not in collections:
                    self._client.create_collection(
                        collection_name=self._collection,
                        vectors_config=qmodels.VectorParams(
                            size=len(point.denseVector),
                            distance=qmodels.Distance.COSINE
                        )
                    )
                self._client.upsert(
                    collection_name=self._collection,
                    points=[
                        qmodels.PointStruct(
                            id=abs(hash(point.chunkId)) % (2**63 - 1),
                            vector=list(point.denseVector),
                            payload={
                                "chunkId": point.chunkId,
                                "documentId": point.documentId,
                                "tenantId": point.tenantId,
                                "version": point.version,
                                "sectionTitle": point.sectionTitle,
                                "content": point.content,
                                "aclTags": list(point.aclTags),
                                "metadata": point.metadata,
                                "createdAt": point.createdAt
                            }
                        )
                    ]
                )
            except Exception:
                pass

    async def search_dense(
        self,
        tenant_id: str,
        vector: Sequence[float],
        permission_scope: PermissionScope,
        limit: int
    ) -> Result[Sequence[EnrichedChunkVectorDTO], ApplicationError]:
        if self._client:
            try:
                from qdrant_client.http import models as qmodels
                filter_conditions = [
                    qmodels.FieldCondition(key="tenantId", match=qmodels.MatchValue(value=tenant_id))
                ]
                hits = self._client.search(
                    collection_name=self._collection,
                    query_vector=list(vector),
                    query_filter=qmodels.Filter(must=filter_conditions),
                    limit=limit
                )
                if hits:
                    results = []
                    for h in hits:
                        p = h.payload
                        if any(acl in permission_scope.allowedAcls for acl in p.get("aclTags", [])):
                            results.append(
                                EnrichedChunkVectorDTO(
                                    chunkId=p["chunkId"],
                                    documentId=p["documentId"],
                                    tenantId=p["tenantId"],
                                    version=p["version"],
                                    sectionTitle=p["sectionTitle"],
                                    content=p["content"],
                                    denseVector=vector,
                                    sparseVector=None,
                                    aclTags=p.get("aclTags", ["PUBLIC"]),
                                    metadata=p.get("metadata", {}),
                                    createdAt=p.get("createdAt", "")
                                )
                            )
                    if results:
                        return Ok(tuple(results))
            except Exception:
                pass
        return await self._fallback.search_dense(tenant_id, vector, permission_scope, limit)

    async def search_sparse(
        self,
        tenant_id: str,
        indices: Sequence[int],
        values: Sequence[float],
        permission_scope: PermissionScope,
        limit: int
    ) -> Result[Sequence[EnrichedChunkVectorDTO], ApplicationError]:
        return await self._fallback.search_sparse(tenant_id, indices, values, permission_scope, limit)
