-- migration:      0002
-- description:    create kafka offsets tracking ledger for exactly-once ingestion deduplication
-- author:         rag-pipeline-architect
-- date:           2026-10-27
-- depends_on:     0001
-- reversible:     YES
-- lock_risk:      LOW
-- rows_affected:  schema only
-- reason:         support resilient exactly-once kafka consumer offset tracking across pipeline restarts

CREATE TABLE IF NOT EXISTS kafka_consumer_offsets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic VARCHAR(128) NOT NULL,
    partition_id INTEGER NOT NULL,
    consumer_group VARCHAR(128) NOT NULL,
    committed_offset BIGINT NOT NULL,
    leader_epoch INTEGER DEFAULT NULL,
    metadata TEXT DEFAULT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT kafka_offsets_topic_length_ck CHECK (char_length(btrim(topic)) >= 1),
    CONSTRAINT kafka_offsets_group_length_ck CHECK (char_length(btrim(consumer_group)) >= 1),
    CONSTRAINT kafka_offsets_partition_positive_ck CHECK (partition_id >= 0),
    CONSTRAINT kafka_offsets_committed_offset_positive_ck CHECK (committed_offset >= 0),
    CONSTRAINT kafka_offsets_topic_partition_group_uk UNIQUE (topic, partition_id, consumer_group)
);

CREATE INDEX IF NOT EXISTS idx_kafka_offsets_lookup 
    ON kafka_consumer_offsets(topic, partition_id, consumer_group);
