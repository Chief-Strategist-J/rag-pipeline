INSERT INTO documents (
    id,
    tenant_id,
    title,
    uri,
    mime_type,
    content_hash,
    raw_content,
    metadata,
    created_at,
    updated_at
) VALUES (
    'doc-seed-test-001',
    'tenant-test',
    'Test Coverage Specification',
    's3://test-docs/test-spec.md',
    'text/markdown',
    'sha256:d41d8cd98f00b204e9800998ecf8427e',
    '# Test Coverage Specification\n\nAll test suites must verify invariants.',
    '{"author": "QA Team", "category": "testing"}',
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;
