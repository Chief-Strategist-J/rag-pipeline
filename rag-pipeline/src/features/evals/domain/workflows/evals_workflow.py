from src.features.evals.contracts.evals_types import (
    RetrievalEvalInputDTO,
    AnswerEvalInputDTO,
    EvaluationReportDTO,
)
from src.features.evals.infrastructure.ports.evals_ports import EvalMetricStoragePort
from src.features.evals.domain.rules.evals_rules import (
    compute_recall_at_k,
    compute_mrr,
    compute_faithfulness_overlap,
)
from src.features.evals.domain.machines.evals_machine import (
    EvalState,
    EvalEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class EvalsWorkflow:
    def __init__(self, storage_port: EvalMetricStoragePort) -> None:
        self._storage = storage_port

    async def execute(
        self,
        retrieval_input: RetrievalEvalInputDTO,
        answer_input: AnswerEvalInputDTO
    ) -> Result[EvaluationReportDTO, ApplicationError]:
        state = EvalState.INITIALIZED

        t_ret = transition_state(state, EvalEvent.EVAL_RETRIEVAL)
        if not t_ret.is_ok:
            return Err(t_ret.error)
        state = t_ret.value

        recall = compute_recall_at_k(
            retrieved_ids=retrieval_input.retrievedChunkIds,
            golden_ids=retrieval_input.goldenRelevantChunkIds,
            k=retrieval_input.k
        )
        mrr = compute_mrr(
            retrieved_ids=retrieval_input.retrievedChunkIds,
            golden_ids=retrieval_input.goldenRelevantChunkIds
        )

        t_ans = transition_state(state, EvalEvent.EVAL_ANSWER)
        if not t_ans.is_ok:
            return Err(t_ans.error)
        state = t_ans.value

        faithfulness = compute_faithfulness_overlap(
            answer=answer_input.answer,
            context_text=answer_input.contextText
        )
        is_abstain_appropriate = (
            answer_input.abstained and len(retrieval_input.goldenRelevantChunkIds) == 0
        ) or (not answer_input.abstained and len(retrieval_input.goldenRelevantChunkIds) > 0)

        t_agg = transition_state(state, EvalEvent.AGGREGATE)
        if not t_agg.is_ok:
            return Err(t_agg.error)
        state = t_agg.value

        report = EvaluationReportDTO(
            tenantId=retrieval_input.tenantId,
            queryId=retrieval_input.queryId,
            recallAtK=recall,
            mrr=mrr,
            faithfulnessScore=faithfulness,
            isAbstainAppropriate=is_abstain_appropriate,
            evaluationStatus="PASS" if (recall >= 0.5 and faithfulness >= 0.5) else "NEEDS_TUNING",
            correlationId=retrieval_input.correlationId
        )

        record_res = await self._storage.record_eval_report(report)
        if not record_res.is_ok:
            return Err(record_res.error)

        t_comp = transition_state(state, EvalEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(report)
