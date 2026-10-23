from typing import Protocol, Sequence, Tuple
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class VectorEmbeddingModelPort(Protocol):
    async def generate_dense_embeddings(
        self,
        texts: Sequence[str]
    ) -> Result[Sequence[Sequence[float]], ApplicationError]:
        ...


class SparseEncodingPort(Protocol):
    async def generate_sparse_vectors(
        self,
        texts: Sequence[str]
    ) -> Result[Sequence[Tuple[Sequence[int], Sequence[float]]], ApplicationError]:
        ...
