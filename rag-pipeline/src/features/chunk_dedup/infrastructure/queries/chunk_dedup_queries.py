FLOW_INSERT_CHUNK_FINGERPRINT = """
INSERT INTO chunk_fingerprints (
    id,
    public_id,
    tenant_id,
    document_id,
    version,
    content_hash,
    created_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :document_id,
    :version,
    :content_hash,
    NOW()
);
"""

FLOW_SELECT_CHUNK_VERSION_BY_HASH = """
SELECT version
FROM chunk_fingerprints
WHERE tenant_id = :tenant_id AND content_hash = :content_hash
ORDER BY version DESC
LIMIT 1;
"""
