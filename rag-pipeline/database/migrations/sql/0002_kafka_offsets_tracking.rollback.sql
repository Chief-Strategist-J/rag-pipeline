-- migration:      0002
-- description:    rollback kafka offsets tracking ledger
-- author:         rag-pipeline-architect
-- date:           2026-10-27
-- depends_on:     0001
-- reversible:     YES
-- lock_risk:      LOW
-- rows_affected:  schema only
-- reason:         clean rollback of 0002 kafka consumer offsets tracking table

DROP INDEX IF EXISTS idx_kafka_offsets_lookup;
DROP TABLE IF EXISTS kafka_consumer_offsets;
