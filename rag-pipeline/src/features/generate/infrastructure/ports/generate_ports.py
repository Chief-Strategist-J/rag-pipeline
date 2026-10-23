from typing import Protocol, Tuple
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class LlmInferencePort(Protocol):
    async def generate_completion(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Result[Tuple[str, int, int, str], ApplicationError]:
        ...
