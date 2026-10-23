from typing import Sequence, List
from src.features.rerank.infrastructure.ports.rerank_ports import CrossEncoderModelPort
from src.features.rerank.domain.rules.rerank_rules import sigmoid_normalize
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class BgeRerankerAdapter(CrossEncoderModelPort):
    async def compute_similarity_scores(
        self,
        query: str,
        texts: Sequence[str]
    ) -> Result[Sequence[float], ApplicationError]:
        try:
            scores: List[float] = []
            query_words = set(query.lower().split())
            for text in texts:
                text_words = set(text.lower().split())
                overlap = len(query_words.intersection(text_words))
                raw_score = float(overlap * 2.0)
                norm_score = sigmoid_normalize(raw_score)
                scores.append(norm_score)
            return Ok(tuple(scores))
        except Exception as err:
            return Err(ApplicationError(str(err), code="RERANK_SCORING_FAILED", status_code=500))
