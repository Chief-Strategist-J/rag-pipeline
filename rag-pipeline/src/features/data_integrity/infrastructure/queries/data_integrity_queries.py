FLOW_CHECK_ORDERS_ORPHAN_TENANT = """
SELECT id, tenant_id FROM orders o
WHERE NOT EXISTS (SELECT 1 FROM tenants t WHERE t.id = o.tenant_id);
"""

FLOW_CHECK_ORDERS_SHIPPED_DISAGREEMENT = """
SELECT id, tenant_id, status, shipped_at FROM orders
WHERE (status = 'shipped') <> (shipped_at IS NOT NULL);
"""

FLOW_CHECK_ORDERS_NEGATIVE_AMOUNT = """
SELECT id, tenant_id, amount FROM orders
WHERE amount < 0;
"""

FLOW_CHECK_ORDERS_DUPLICATE_EXTERNAL_NATURAL_KEY = """
SELECT tenant_id, source, external_id, count(*)
FROM orders
GROUP BY tenant_id, source, external_id
HAVING count(*) > 1;
"""
