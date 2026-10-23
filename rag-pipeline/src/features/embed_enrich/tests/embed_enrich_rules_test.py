import pytest
from src.features.embed_enrich.domain.rules.embed_enrich_rules import (
    normalize_dense_vector,
    build_lexical_sparse_representation,
)
from src.features.embed_enrich.domain.machines.embed_enrich_machine import (
    EmbedEnrichState,
    EmbedEnrichEvent,
    transition_state,
)


def test_embed_enrich_rules():
    raw_vec = [3.0, 4.0]
    norm_vec = normalize_dense_vector(raw_vec)
    assert norm_vec == (0.6, 0.8)

    indices, values = build_lexical_sparse_representation("error ERR_404 not found in cluster")
    assert len(indices) == len(values)
    assert len(indices) == 6


def test_embed_enrich_state_transitions():
    t1 = transition_state(EmbedEnrichState.INITIALIZED, EmbedEnrichEvent.EMBED_DENSE)
    assert t1.is_ok is True
    assert t1.value == EmbedEnrichState.DENSE_EMBEDDING

    t2 = transition_state(t1.value, EmbedEnrichEvent.ENCODE_SPARSE)
    assert t2.is_ok is True
    assert t2.value == EmbedEnrichState.SPARSE_ENCODING

    t3 = transition_state(t2.value, EmbedEnrichEvent.ATTACH_METADATA)
    assert t3.is_ok is True
    assert t3.value == EmbedEnrichState.ENRICHING_METADATA

    t4 = transition_state(t3.value, EmbedEnrichEvent.COMPLETE)
    assert t4.is_ok is True
    assert t4.value == EmbedEnrichState.COMPLETED
