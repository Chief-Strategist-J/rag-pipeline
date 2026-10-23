from src.features.index.contracts.index_types import (
    IndexUpsertRequestDTO,
    IndexUpsertResultDTO,
    IndexCollectionMetaDTO,
    CollectionStatus,
)
from src.features.index.infrastructure.ports.index_ports import (
    QdrantCollectionPort,
    IndexMetadataRegistryPort,
)
from src.features.index.domain.rules.index_rules import format_collection_name
from src.features.index.domain.machines.index_machine import (
    IndexLifecycleState,
    IndexLifecycleEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError
from src.shared.utils.time_utils import utc_now_iso


class IndexWorkflow:
    def __init__(
        self,
        qdrant_port: QdrantCollectionPort,
        registry_port: IndexMetadataRegistryPort
    ) -> None:
        self._qdrant = qdrant_port
        self._registry = registry_port

    async def execute(
        self,
        request: IndexUpsertRequestDTO
    ) -> Result[IndexUpsertResultDTO, ApplicationError]:
        state = IndexLifecycleState.INITIALIZED

        col_name = format_collection_name(request.tenantId, request.collectionVersion)

        t_val = transition_state(state, IndexLifecycleEvent.VALIDATE)
        if not t_val.is_ok:
            return Err(t_val.error)
        state = t_val.value

        first_dim = len(request.vectors[0].denseVector) if request.vectors else 1024
        ensure_res = await self._qdrant.ensure_collection_exists(col_name, dimension=first_dim)
        if not ensure_res.is_ok:
            return Err(ensure_res.error)

        t_up = transition_state(state, IndexLifecycleEvent.UPSERT)
        if not t_up.is_ok:
            return Err(t_up.error)
        state = t_up.value

        upsert_res = await self._qdrant.upsert_points(col_name, request.vectors)
        if not upsert_res.is_ok:
            return Err(upsert_res.error)
        upserted_count = upsert_res.value

        t_sync = transition_state(state, IndexLifecycleEvent.SYNC)
        if not t_sync.is_ok:
            return Err(t_sync.error)
        state = t_sync.value

        meta = IndexCollectionMetaDTO(
            collectionName=col_name,
            tenantId=request.tenantId,
            version=request.collectionVersion,
            dimension=first_dim,
            status=CollectionStatus.ACTIVE,
            isPrimary=True,
            totalPoints=upserted_count,
            createdAt=utc_now_iso()
        )
        sync_res = await self._registry.update_collection_meta(meta)
        if not sync_res.is_ok:
            return Err(sync_res.error)

        t_comp = transition_state(state, IndexLifecycleEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(
            IndexUpsertResultDTO(
                collectionName=col_name,
                tenantId=request.tenantId,
                upsertedCount=upserted_count,
                status="ACTIVE",
                correlationId=request.correlationId
            )
        )
