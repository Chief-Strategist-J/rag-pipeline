from typing import Protocol
from src.features.generate.contracts.generate_types import (
    GenerationRequestDTO,
    GenerationResponseDTO,
)
from src.features.generate.infrastructure.ports.generate_ports import LlmInferencePort
from src.features.generate.domain.workflows.generate_workflow import GenerateWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class GenerateServiceDeps(Protocol):
    llm_port: LlmInferencePort


class GenerateService:
    def __init__(self, deps: GenerateServiceDeps) -> None:
        self._workflow = GenerateWorkflow(llm_port=deps.llm_port)

    async def generate_answer(
        self,
        request: GenerationRequestDTO
    ) -> Result[GenerationResponseDTO, ApplicationError]:
        try:
            return await self._workflow.execute(request)
        except Exception as err:
            return Err(ApplicationError(str(err), code="GENERATE_SERVICE_ERROR", status_code=500))
