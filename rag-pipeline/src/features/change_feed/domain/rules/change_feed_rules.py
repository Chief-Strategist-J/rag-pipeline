from src.features.change_feed.contracts.change_feed_types import (
    DocumentChangeEventDTO,
    ChangeOperation,
)


def is_deletion_or_acl_change(event: DocumentChangeEventDTO) -> bool:
    return event.operation in (ChangeOperation.DELETE, ChangeOperation.ACL_UPDATE)


def requires_immediate_cache_purge(event: DocumentChangeEventDTO) -> bool:
    return event.operation == ChangeOperation.DELETE


def is_valid_version_sequence(current_version: int, incoming_version: int) -> bool:
    return incoming_version > current_version
