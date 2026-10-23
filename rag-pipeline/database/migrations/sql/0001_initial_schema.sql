-- migration:      0001
-- description:    initial schema for multi-tenant authz and rag pipeline audit
-- author:         rag-pipeline-architect
-- date:           2026-10-23
-- depends_on:     NONE
-- reversible:     YES
-- lock_risk:      LOW
-- rows_affected:  schema only
-- reason:         scaffold core multi-tenant storage gate and tables

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    public_id VARCHAR(64) NOT NULL UNIQUE,
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 1,
    CONSTRAINT tenants_status_ck CHECK (status IN ('ACTIVE', 'SUSPENDED', 'ARCHIVED')),
    CONSTRAINT tenants_name_length_ck CHECK (char_length(btrim(name)) >= 1),
    CONSTRAINT tenants_code_format_ck CHECK (code ~ '^[a-z0-9_-]+$')
);

CREATE TABLE IF NOT EXISTS permission_scopes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    public_id VARCHAR(64) NOT NULL UNIQUE,
    tenant_id UUID NOT NULL,
    user_id VARCHAR(128) NOT NULL,
    allowed_acls TEXT[] NOT NULL DEFAULT ARRAY['INTERNAL', 'PUBLIC'],
    allowed_partitions TEXT[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 1,
    CONSTRAINT permission_scopes_tenant_fk FOREIGN KEY (tenant_id)
        REFERENCES tenants(id) ON DELETE RESTRICT,
    CONSTRAINT permission_scopes_tenant_id_uk UNIQUE (tenant_id, id),
    CONSTRAINT permission_scopes_tenant_user_uk UNIQUE (tenant_id, user_id),
    CONSTRAINT permission_scopes_user_id_check CHECK (char_length(btrim(user_id)) >= 1)
);

CREATE TABLE IF NOT EXISTS query_rewrite_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    public_id VARCHAR(64) NOT NULL UNIQUE,
    tenant_id UUID NOT NULL,
    user_id VARCHAR(128) NOT NULL,
    request_id VARCHAR(128) NOT NULL,
    correlation_id UUID NOT NULL,
    original_query TEXT NOT NULL,
    rewritten_query TEXT NOT NULL,
    was_rewritten BOOLEAN NOT NULL,
    latency_ms INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 1,
    CONSTRAINT query_rewrite_audit_tenant_fk FOREIGN KEY (tenant_id)
        REFERENCES tenants(id) ON DELETE RESTRICT,
    CONSTRAINT query_rewrite_audit_tenant_id_uk UNIQUE (tenant_id, id),
    CONSTRAINT query_rewrite_audit_latency_nonneg_ck CHECK (latency_ms >= 0),
    CONSTRAINT query_rewrite_audit_orig_query_ck CHECK (char_length(btrim(original_query)) >= 1),
    CONSTRAINT query_rewrite_audit_rewritten_query_ck CHECK (char_length(btrim(rewritten_query)) >= 1)
);

CREATE INDEX IF NOT EXISTS idx_tenants_status ON tenants(status);
CREATE INDEX IF NOT EXISTS idx_perm_scopes_tenant_user ON permission_scopes(tenant_id, user_id);
CREATE INDEX IF NOT EXISTS idx_rewrite_audit_req ON query_rewrite_audit_logs(request_id);
CREATE INDEX IF NOT EXISTS idx_rewrite_audit_tenant_corr ON query_rewrite_audit_logs(tenant_id, correlation_id);
