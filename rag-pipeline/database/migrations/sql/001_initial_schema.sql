CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 1,
    CONSTRAINT tenants_status_ck CHECK (status IN ('ACTIVE', 'SUSPENDED', 'ARCHIVED'))
);

CREATE TABLE IF NOT EXISTS permission_scopes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id VARCHAR(128) NOT NULL,
    allowed_acls TEXT[] NOT NULL DEFAULT ARRAY['INTERNAL', 'PUBLIC'],
    allowed_partitions TEXT[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 1,
    CONSTRAINT permission_scopes_tenant_fk FOREIGN KEY (tenant_id)
        REFERENCES tenants(id) ON DELETE RESTRICT,
    CONSTRAINT permission_scopes_tenant_user_uk UNIQUE (tenant_id, user_id)
);

CREATE TABLE IF NOT EXISTS query_rewrite_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id VARCHAR(128) NOT NULL,
    request_id VARCHAR(128) NOT NULL,
    correlation_id VARCHAR(128),
    original_query TEXT NOT NULL,
    rewritten_query TEXT NOT NULL,
    was_rewritten BOOLEAN NOT NULL,
    latency_ms INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT query_rewrite_audit_tenant_fk FOREIGN KEY (tenant_id)
        REFERENCES tenants(id) ON DELETE RESTRICT,
    CONSTRAINT query_rewrite_audit_latency_ck CHECK (latency_ms >= 0)
);

CREATE INDEX IF NOT EXISTS idx_perm_scopes_tenant_user ON permission_scopes(tenant_id, user_id);
CREATE INDEX IF NOT EXISTS idx_rewrite_audit_req ON query_rewrite_audit_logs(request_id);
