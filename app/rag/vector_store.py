from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Sequence

import numpy as np

from .chunker import Chunk


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float


def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype="float32")
    if matrix.ndim == 1:
        matrix = matrix.reshape(1, -1)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class NumpyVectorStore:
    """Store em memória usado nos testes do pipeline."""

    def __init__(self, embeddings: np.ndarray, chunks: Sequence[Chunk]) -> None:
        matrix = _normalize_rows(embeddings)
        if len(matrix) != len(chunks):
            raise ValueError("Quantidade de embeddings e chunks deve ser igual")
        self.embeddings = matrix
        self.chunks = list(chunks)

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[SearchHit]:
        query = _normalize_rows(query_embedding)[0]
        scores = self.embeddings @ query
        order = np.argsort(scores)[::-1][: min(top_k, len(self.chunks))]
        return [SearchHit(self.chunks[int(i)], float(scores[int(i)])) for i in order]


class FaissVectorStore:
    """Índice vetorial persistente baseado em FAISS e similaridade cosseno."""

    INDEX_FILENAME = "index.faiss"
    METADATA_FILENAME = "metadata.json"

    def __init__(self, index, chunks: Sequence[Chunk], dimension: int) -> None:
        self.index = index
        self.chunks = list(chunks)
        self.dimension = dimension

    @staticmethod
    def _faiss():
        try:
            import faiss
        except ImportError as exc:
            raise RuntimeError(
                "FAISS não está instalado. Execute: pip install -r requirements.txt"
            ) from exc
        return faiss

    @classmethod
    def build(cls, embeddings: np.ndarray, chunks: Sequence[Chunk]) -> "FaissVectorStore":
        matrix = _normalize_rows(embeddings)
        if matrix.ndim != 2 or matrix.shape[0] == 0:
            raise ValueError("É necessário pelo menos um embedding para criar o índice")
        if matrix.shape[0] != len(chunks):
            raise ValueError("Quantidade de embeddings e chunks deve ser igual")

        faiss = cls._faiss()
        dimension = int(matrix.shape[1])
        index = faiss.IndexFlatIP(dimension)
        index.add(matrix.astype("float32"))
        return cls(index=index, chunks=chunks, dimension=dimension)

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[SearchHit]:
        query = _normalize_rows(query_embedding)
        if query.shape[1] != self.dimension:
            raise ValueError(
                f"Query com dimensão {query.shape[1]}; índice usa {self.dimension}"
            )

        k = min(top_k, len(self.chunks))
        scores, indices = self.index.search(query.astype("float32"), k)

        hits: list[SearchHit] = []
        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue
            hits.append(SearchHit(chunk=self.chunks[int(index)], score=float(score)))
        return hits

    def save(self, directory: str | Path) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        faiss = self._faiss()
        faiss.write_index(self.index, str(directory / self.INDEX_FILENAME))

        payload = {
            "dimension": self.dimension,
            "chunks": [asdict(chunk) for chunk in self.chunks],
        }
        (directory / self.METADATA_FILENAME).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, directory: str | Path) -> "FaissVectorStore":
        directory = Path(directory)
        index_path = directory / cls.INDEX_FILENAME
        metadata_path = directory / cls.METADATA_FILENAME

        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                "Índice vetorial não encontrado. Execute: python scripts/build_index.py"
            )

        faiss = cls._faiss()
        index = faiss.read_index(str(index_path))
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        chunks = [Chunk(**item) for item in payload["chunks"]]
        dimension = int(payload["dimension"])
        return cls(index=index, chunks=chunks, dimension=dimension)
