FLOW_INSERT_CHANGE_FEED_EVENT = """
INSERT INTO document_change_events (
    id,
    public_id,
    tenant_id,
    document_id,
    event_id,
    operation,
    version,
    source,
    content,
    acl_tags,
    metadata,
    correlation_id,
    status,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :document_id,
    :event_id,
    :operation,
    :version,
    :source,
    :content,
    :acl_tags,
    :metadata,
    :correlation_id,
    'RECEIVED',
    NOW(),
    NOW()
);
"""

FLOW_SELECT_DOCUMENT_LATEST_VERSION = """
SELECT version
FROM document_change_events
WHERE tenant_id = :tenant_id AND document_id = :document_id
ORDER BY version DESC
LIMIT 1;
"""
