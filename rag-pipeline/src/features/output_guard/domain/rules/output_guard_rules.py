from typing import Sequence, Tuple, List
import re


def strip_markdown_images_and_links(text: str) -> Tuple[str, int]:
    img_pattern = r"!\[([^\]]*)\]\([^\)]+\)"
    cleaned, img_count = re.subn(img_pattern, r"[\1]", text)

    link_pattern = r"\[([^\]]+)\]\((https?://[^\)]+)\)"
    cleaned, link_count = re.subn(link_pattern, r"\1", cleaned)

    return cleaned, (img_count + link_count)


def validate_citations(
    cited_chunk_ids: Sequence[str],
    allowed_chunk_ids: Sequence[str]
) -> Tuple[List[str], List[str]]:
    allowed_set = set(allowed_chunk_ids)
    valid: List[str] = []
    hallucinated: List[str] = []

    for cid in cited_chunk_ids:
        if cid in allowed_set:
            valid.append(cid)
        else:
            hallucinated.append(cid)

    return sorted(valid), sorted(hallucinated)
