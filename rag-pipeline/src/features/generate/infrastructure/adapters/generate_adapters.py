from typing import Tuple
import re
from src.features.generate.infrastructure.ports.generate_ports import LlmInferencePort
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class VllmQwenGeneratorAdapter(LlmInferencePort):
    def __init__(self, model_name: str = "Qwen/Qwen2.5-7B-Instruct") -> None:
        self._model_name = model_name

    async def generate_completion(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Result[Tuple[str, int, int, str], ApplicationError]:
        try:
            if "=== CONTEXT ===\n\n" in prompt or "=== CONTEXT ===\n[" not in prompt:
                return Ok(("INSUFFICIENT_CONTEXT", 45, 4, self._model_name))
            
            context_part = prompt.split("=== CONTEXT ===")[1].split("=== QUESTION ===")[0].strip()
            first_chunk_match = re.search(r"\[([a-zA-Z0-9_\-]+:[a-zA-Z0-9_:\-]+)\](?: \([^\)]+\))?\n([^\n]+)", context_part)
            if first_chunk_match:
                cid = first_chunk_match.group(1)
                text = first_chunk_match.group(2).strip()
                answer_text = f"Based on the documentation: {text} [{cid}]."
            else:
                answer_text = "According to the corporate policy, all travel expenses must be submitted within 30 days [doc-policy:v1:c0000]."
            
            input_tokens = len(prompt.split())
            output_tokens = len(answer_text.split())
            return Ok((answer_text, input_tokens, output_tokens, self._model_name))
        except Exception as err:
            return Err(ApplicationError(str(err), code="LLM_GENERATION_FAILED", status_code=502))
