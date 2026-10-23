from typing import Sequence, Dict, Optional
from src.features.index.infrastructure.ports.index_ports import (
    QdrantCollectionPort,
    IndexMetadataRegistryPort,
)
from src.features.index.contracts.index_types import (
    IndexCollectionMetaDTO,
    CollectionStatus,
)
from src.features.embed_enrich.contracts.embed_enrich_types import EnrichedChunkVectorDTO
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class MemoryQdrantCollectionAdapter(QdrantCollectionPort):
    def __init__(self) -> None:
        self.collections: Dict[str, Dict[str, EnrichedChunkVectorDTO]] = {}

    async def ensure_collection_exists(
        self,
        collection_name: str,
        dimension: int
    ) -> Result[bool, ApplicationError]:
        if collection_name not in self.collections:
            self.collections[collection_name] = {}
        return Ok(True)

    async def upsert_points(
        self,
        collection_name: str,
        points: Sequence[EnrichedChunkVectorDTO]
    ) -> Result[int, ApplicationError]:
        if collection_name not in self.collections:
            self.collections[collection_name] = {}
        for p in points:
            self.collections[collection_name][p.chunkId] = p
        return Ok(len(points))


class MemoryIndexMetadataRegistryAdapter(IndexMetadataRegistryPort):
    def __init__(self) -> None:
        self.registry: Dict[str, IndexCollectionMetaDTO] = {}

    async def get_collection_meta(
        self,
        collection_name: str
    ) -> Result[Optional[IndexCollectionMetaDTO], ApplicationError]:
        return Ok(self.registry.get(collection_name))

    async def update_collection_meta(
        self,
        meta: IndexCollectionMetaDTO
    ) -> Result[bool, ApplicationError]:
        self.registry[meta.collectionName] = meta
        return Ok(True)
