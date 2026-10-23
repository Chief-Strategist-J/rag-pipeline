FLOW_INSERT_EMBEDDED_CHUNK = """
INSERT INTO chunk_embeddings (
    id,
    public_id,
    tenant_id,
    document_id,
    chunk_id,
    version,
    acl_tags,
    created_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :document_id,
    :chunk_id,
    :version,
    :acl_tags,
    NOW()
);
"""

FLOW_SELECT_EMBEDDED_CHUNKS_BY_DOC = """
SELECT id, public_id, tenant_id, document_id, chunk_id, version, acl_tags
FROM chunk_embeddings
WHERE tenant_id = :tenant_id AND document_id = :document_id
ORDER BY created_at ASC;
"""
