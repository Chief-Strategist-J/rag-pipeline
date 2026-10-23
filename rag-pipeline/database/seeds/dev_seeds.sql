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
    'doc-seed-dev-001',
    'tenant-dev',
    'Development Handbook',
    's3://internal-docs/dev-handbook.md',
    'text/markdown',
    'sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    '# Development Handbook\n\nGuidelines for running development clusters.',
    '{"author": "Architecture Team", "category": "engineering"}',
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;
