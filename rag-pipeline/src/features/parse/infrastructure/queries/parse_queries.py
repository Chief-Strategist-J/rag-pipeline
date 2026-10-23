FLOW_INSERT_PARSED_DOCUMENT_SUMMARY = """
INSERT INTO parsed_documents (
    id,
    public_id,
    tenant_id,
    document_id,
    format,
    total_blocks,
    has_tables,
    correlation_id,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :document_id,
    :format,
    :total_blocks,
    :has_tables,
    :correlation_id,
    NOW(),
    NOW()
);
"""

FLOW_SELECT_PARSED_DOCUMENT_BY_ID = """
SELECT id, public_id, tenant_id, document_id, format, total_blocks, has_tables, correlation_id
FROM parsed_documents
WHERE tenant_id = :tenant_id AND document_id = :document_id
LIMIT 1;
"""
