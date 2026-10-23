FLOW_INSERT_COLLECTION_VERSION = """
INSERT INTO index_collection_versions (
    id,
    public_id,
    tenant_id,
    collection_name,
    version,
    dimension,
    status,
    is_primary,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :collection_name,
    :version,
    :dimension,
    :status,
    :is_primary,
    NOW(),
    NOW()
);
"""

FLOW_SELECT_PRIMARY_COLLECTION_FOR_TENANT = """
SELECT collection_name, version, status
FROM index_collection_versions
WHERE tenant_id = :tenant_id AND is_primary = TRUE
LIMIT 1;
"""
