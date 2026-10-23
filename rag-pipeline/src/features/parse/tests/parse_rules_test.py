import pytest
from src.features.parse.contracts.parse_types import (
    ParsedBlockDTO,
    BlockType,
)
from src.features.parse.domain.rules.parse_rules import (
    contains_tabular_content,
    has_valid_structural_headings,
)
from src.features.parse.domain.machines.parse_machine import (
    ParseState,
    ParseEvent,
    transition_state,
)


def test_parse_rules():
    blocks = [
        ParsedBlockDTO(
            blockId="b1",
            blockType=BlockType.HEADING,
            content="Architecture Overview",
            headingLevel=1
        ),
        ParsedBlockDTO(
            blockId="b2",
            blockType=BlockType.TABLE,
            content="| Field | Type |",
            tableMatrix=[["Field", "Type"]]
        ),
    ]
    assert contains_tabular_content(blocks) is True
    assert has_valid_structural_headings(blocks) is True


def test_parse_state_transitions():
    t1 = transition_state(ParseState.INITIALIZED, ParseEvent.INGEST)
    assert t1.is_ok is True
    assert t1.value == ParseState.INGESTED

    t2 = transition_state(t1.value, ParseEvent.PARSE)
    assert t2.is_ok is True
    assert t2.value == ParseState.PARSING

    t3 = transition_state(t2.value, ParseEvent.STRUCTURE)
    assert t3.is_ok is True
    assert t3.value == ParseState.STRUCTURED

    t4 = transition_state(t3.value, ParseEvent.COMPLETE)
    assert t4.is_ok is True
    assert t4.value == ParseState.COMPLETED
