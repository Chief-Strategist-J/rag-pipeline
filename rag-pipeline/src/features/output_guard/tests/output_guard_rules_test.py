import pytest
from src.features.output_guard.domain.rules.output_guard_rules import (
    strip_markdown_images_and_links,
    validate_citations,
)
from src.features.output_guard.domain.machines.output_guard_machine import (
    OutputGuardState,
    OutputGuardEvent,
    transition_state,
)


def test_markdown_sanitization_rules():
    raw_markdown = "See the chart ![exfil](http://malicious.com/tracker.png) or visit [Link](https://phish.org/login)."
    clean_text, removed_count = strip_markdown_images_and_links(raw_markdown)
    assert "http://malicious.com" not in clean_text
    assert "https://phish.org" not in clean_text
    assert removed_count == 2


def test_citation_validation_rules():
    cited = ["chunk_1", "chunk_fabricated", "chunk_2"]
    allowed = ["chunk_1", "chunk_2", "chunk_3"]
    valid, hallucinated = validate_citations(cited, allowed)
    assert valid == ["chunk_1", "chunk_2"]
    assert hallucinated == ["chunk_fabricated"]


def test_output_guard_state_machine():
    t1 = transition_state(OutputGuardState.INITIALIZED, OutputGuardEvent.SANITIZE)
    assert t1.is_ok is True
    assert t1.value == OutputGuardState.SANITIZING_MARKDOWN

    t2 = transition_state(t1.value, OutputGuardEvent.INSPECT_CITATIONS)
    assert t2.is_ok is True
    assert t2.value == OutputGuardState.INSPECTING_CITATIONS

    t3 = transition_state(t2.value, OutputGuardEvent.EVALUATE)
    assert t3.is_ok is True
    assert t3.value == OutputGuardState.EVALUATING_GROUNDING

    t4 = transition_state(t3.value, OutputGuardEvent.COMPLETE)
    assert t4.is_ok is True
    assert t4.value == OutputGuardState.COMPLETED
