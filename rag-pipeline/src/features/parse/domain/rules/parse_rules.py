from src.features.parse.contracts.parse_types import (
    ParseRequestDTO,
    ParsedBlockDTO,
    BlockType,
)


def contains_tabular_content(blocks: list[ParsedBlockDTO]) -> bool:
    return any(b.blockType == BlockType.TABLE for b in blocks)


def has_valid_structural_headings(blocks: list[ParsedBlockDTO]) -> bool:
    return any(b.blockType == BlockType.HEADING for b in blocks)
