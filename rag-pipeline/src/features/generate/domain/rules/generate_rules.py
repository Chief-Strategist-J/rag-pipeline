from typing import Sequence, List
import re
from src.features.rerank.contracts.rerank_types import RerankedChunkDTO


STATIC_SYSTEM_PROMPT = """You are a strictly factual enterprise assistant.
Answer the question ONLY based on the provided context passages below.
For every factual claim, cite the source chunk ID in brackets like [chunk_id].
If the provided context does not contain sufficient information to answer the question, state: "INSUFFICIENT_CONTEXT"."""


def build_generation_prompt(query: str, context_chunks: Sequence[RerankedChunkDTO]) -> str:
    passages = []
    for chunk in context_chunks:
        passages.append(f"[{chunk.chunkId}] (Section: {chunk.sectionTitle})\n{chunk.content}")
    formatted_context = "\n\n".join(passages)
    return f"{STATIC_SYSTEM_PROMPT}\n\n=== CONTEXT ===\n{formatted_context}\n\n=== QUESTION ===\n{query}\n\n=== ANSWER ==="


def extract_cited_chunk_ids(answer_text: str) -> List[str]:
    pattern = r"\[([a-zA-Z0-9_\-]+:[a-zA-Z0-9_:\-]+)\]"
    matches = re.findall(pattern, answer_text)
    return sorted(list(set(matches)))


def is_abstain_response(answer_text: str) -> bool:
    normalized = answer_text.strip().upper()
    return "INSUFFICIENT_CONTEXT" in normalized or "INSUFFICIENT CONTEXT" in normalized
