from typing import Protocol, Sequence, Tuple
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class CrossEncoderModelPort(Protocol):
    async def compute_similarity_scores(
        self,
        query: str,
        texts: Sequence[str]
    ) -> Result[Sequence[float], ApplicationError]:
        ...
