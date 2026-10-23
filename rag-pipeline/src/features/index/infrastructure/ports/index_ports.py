from typing import Protocol, Sequence, Optional
from src.features.index.contracts.index_types import IndexCollectionMetaDTO
from src.features.embed_enrich.contracts.embed_enrich_types import EnrichedChunkVectorDTO
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class QdrantCollectionPort(Protocol):
    async def ensure_collection_exists(
        self,
        collection_name: str,
        dimension: int
    ) -> Result[bool, ApplicationError]:
        ...

    async def upsert_points(
        self,
        collection_name: str,
        points: Sequence[EnrichedChunkVectorDTO]
    ) -> Result[int, ApplicationError]:
        ...


class IndexMetadataRegistryPort(Protocol):
    async def get_collection_meta(
        self,
        collection_name: str
    ) -> Result[Optional[IndexCollectionMetaDTO], ApplicationError]:
        ...

    async def update_collection_meta(
        self,
        meta: IndexCollectionMetaDTO
    ) -> Result[bool, ApplicationError]:
        ...
