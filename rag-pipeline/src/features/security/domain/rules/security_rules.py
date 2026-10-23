from typing import Sequence, Tuple, List
import re
from src.features.security.contracts.security_types import DetectedThreatDTO, SecurityThreatSeverity

INJECTION_PATTERNS = [
    (r"(?i)ignore\s+(all\s+)?previous\s+instructions", "PROMPT_INJECTION_OVERRIDE", SecurityThreatSeverity.CRITICAL),
    (r"(?i)system\s+prompt\s+override", "PROMPT_INJECTION_OVERRIDE", SecurityThreatSeverity.CRITICAL),
    (r"(?i)disregard\s+(the\s+)?system\s+prompt", "PROMPT_INJECTION_OVERRIDE", SecurityThreatSeverity.HIGH),
    (r"(?i)jailbreak", "PROMPT_INJECTION_JAILBREAK", SecurityThreatSeverity.HIGH),
    (r"(?i)you\s+are\s+now\s+in\s+developer\s+mode", "PROMPT_INJECTION_ROLEPLAY", SecurityThreatSeverity.HIGH),
]


def detect_prompt_injections(text: str) -> List[DetectedThreatDTO]:
    threats: List[DetectedThreatDTO] = []
    for pattern, threat_type, severity in INJECTION_PATTERNS:
        for match in re.finditer(pattern, text):
            threats.append(
                DetectedThreatDTO(
                    threatType=threat_type,
                    severity=severity,
                    matchedPattern=match.group(0),
                    spanOffset=match.start()
                )
            )
    return threats


def neutralize_injections(text: str, threats: Sequence[DetectedThreatDTO]) -> str:
    cleaned = text
    for t in threats:
        cleaned = cleaned.replace(t.matchedPattern, f"[SECURITY_FILTERED: {t.threatType}]")
    return cleaned
