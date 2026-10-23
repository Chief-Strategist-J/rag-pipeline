from typing import Sequence, Tuple, List
from src.features.embed_enrich.infrastructure.ports.embed_enrich_ports import (
    VectorEmbeddingModelPort,
    SparseEncodingPort,
)
from src.features.embed_enrich.domain.rules.embed_enrich_rules import (
    normalize_dense_vector,
    build_lexical_sparse_representation,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class BgeM3EmbeddingAdapter(VectorEmbeddingModelPort):
    def __init__(self, dimension: int = 1024) -> None:
        self._dim = dimension

    async def generate_dense_embeddings(
        self,
        texts: Sequence[str]
    ) -> Result[Sequence[Sequence[float]], ApplicationError]:
        try:
            embeddings: List[Sequence[float]] = []
            for text in texts:
                raw_vec = [float((abs(hash(text + str(i))) % 1000) / 1000.0) for i in range(self._dim)]
                norm_vec = normalize_dense_vector(raw_vec)
                embeddings.append(norm_vec)
            return Ok(tuple(embeddings))
        except Exception as err:
            return Err(ApplicationError(str(err), code="DENSE_EMBEDDING_FAILED", status_code=500))


class LexicalSparseEncodingAdapter(SparseEncodingPort):
    async def generate_sparse_vectors(
        self,
        texts: Sequence[str]
    ) -> Result[Sequence[Tuple[Sequence[int], Sequence[float]]], ApplicationError]:
        try:
            sparse_list: List[Tuple[Sequence[int], Sequence[float]]] = []
            for text in texts:
                indices, values = build_lexical_sparse_representation(text)
                sparse_list.append((indices, values))
            return Ok(tuple(sparse_list))
        except Exception as err:
            return Err(ApplicationError(str(err), code="SPARSE_ENCODING_FAILED", status_code=500))
