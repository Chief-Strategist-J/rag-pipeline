from typing import Sequence, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class RetrievalEvalInputDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    queryId: str
    retrievedChunkIds: Sequence[str]
    goldenRelevantChunkIds: Sequence[str]
    k: int = 5
    correlationId: str


class AnswerEvalInputDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    queryId: str
    query: str
    answer: str
    contextText: str
    abstained: bool
    correlationId: str


class EvaluationReportDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    queryId: str
    recallAtK: float
    mrr: float
    faithfulnessScore: float
    isAbstainAppropriate: bool
    evaluationStatus: str
    correlationId: str
