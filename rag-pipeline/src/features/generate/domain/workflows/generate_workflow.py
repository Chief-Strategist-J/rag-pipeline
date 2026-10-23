from src.features.generate.contracts.generate_types import (
    GenerationRequestDTO,
    GenerationResponseDTO,
)
from src.features.generate.infrastructure.ports.generate_ports import LlmInferencePort
from src.features.generate.domain.rules.generate_rules import (
    build_generation_prompt,
    extract_cited_chunk_ids,
    is_abstain_response,
)
from src.features.generate.domain.machines.generate_machine import (
    GenerateState,
    GenerateEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class GenerateWorkflow:
    def __init__(self, llm_port: LlmInferencePort) -> None:
        self._llm = llm_port

    async def execute(
        self,
        request: GenerationRequestDTO
    ) -> Result[GenerationResponseDTO, ApplicationError]:
        state = GenerateState.INITIALIZED

        t_prompt = transition_state(state, GenerateEvent.BUILD_PROMPT)
        if not t_prompt.is_ok:
            return Err(t_prompt.error)
        state = t_prompt.value

        prompt = build_generation_prompt(query=request.query, context_chunks=request.contextChunks)

        t_infer = transition_state(state, GenerateEvent.INFER)
        if not t_infer.is_ok:
            return Err(t_infer.error)
        state = t_infer.value

        comp_res = await self._llm.generate_completion(
            prompt=prompt,
            temperature=request.temperature,
            max_tokens=request.maxTokens
        )
        if not comp_res.is_ok:
            return Err(comp_res.error)

        answer_text, in_tok, out_tok, model_name = comp_res.value

        t_parse = transition_state(state, GenerateEvent.PARSE)
        if not t_parse.is_ok:
            return Err(t_parse.error)
        state = t_parse.value

        abstained = is_abstain_response(answer_text)
        cited_ids = extract_cited_chunk_ids(answer_text) if not abstained else ()

        t_comp = transition_state(state, GenerateEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(
            GenerationResponseDTO(
                tenantId=request.tenantId,
                query=request.query,
                answer=answer_text,
                abstained=abstained,
                citedChunkIds=tuple(cited_ids),
                inputTokens=in_tok,
                outputTokens=out_tok,
                modelName=model_name,
                correlationId=request.correlationId
            )
        )
