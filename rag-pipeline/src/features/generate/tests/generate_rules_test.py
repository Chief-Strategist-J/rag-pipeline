import pytest
from src.features.generate.domain.rules.generate_rules import (
    build_generation_prompt,
    extract_cited_chunk_ids,
    is_abstain_response,
)
from src.features.generate.domain.machines.generate_machine import (
    GenerateState,
    GenerateEvent,
    transition_state,
)
from src.features.rerank.contracts.rerank_types import RerankedChunkDTO


def test_generate_rules():
    chunks = [
        RerankedChunkDTO(
            chunkId="doc1:c0001",
            documentId="doc1",
            tenantId="t1",
            version=1,
            sectionTitle="Security",
            content="Tokens expire after 1 hour.",
            relevanceScore=0.95,
            originalRank=1,
            rerankedRank=1
        )
    ]
    prompt = build_generation_prompt("When do tokens expire?", chunks)
    assert "=== CONTEXT ===" in prompt
    assert "[doc1:c0001]" in prompt
    assert "=== QUESTION ===" in prompt

    answer = "Tokens expire in 1 hour [doc1:c0001] as per policy [doc2:c0003]."
    cited = extract_cited_chunk_ids(answer)
    assert cited == ["doc1:c0001", "doc2:c0003"]

    assert is_abstain_response("INSUFFICIENT_CONTEXT") is True
    assert is_abstain_response("I have sufficient context") is False


def test_generate_state_machine():
    t1 = transition_state(GenerateState.INITIALIZED, GenerateEvent.BUILD_PROMPT)
    assert t1.is_ok is True
    assert t1.value == GenerateState.BUILDING_PROMPT

    t2 = transition_state(t1.value, GenerateEvent.INFER)
    assert t2.is_ok is True
    assert t2.value == GenerateState.EXECUTING_INFERENCE

    t3 = transition_state(t2.value, GenerateEvent.PARSE)
    assert t3.is_ok is True
    assert t3.value == GenerateState.PARSING_CITATIONS

    t4 = transition_state(t3.value, GenerateEvent.COMPLETE)
    assert t4.is_ok is True
    assert t4.value == GenerateState.COMPLETED
