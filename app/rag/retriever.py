from __future__ import annotations

from typing import Protocol

from app.config import settings
from .embeddings import EmbeddingProvider
from .vector_store import SearchHit


class SearchableVectorStore(Protocol):
    def search(self, query_embedding, top_k: int = 5) -> list[SearchHit]:
        ...


class Retriever:
    def __init__(
        self,
        vector_store: SearchableVectorStore,
        embedder: EmbeddingProvider,
        top_k: int | None = None,
    ) -> None:
        self.vector_store = vector_store
        self.embedder = embedder
        self.top_k = top_k or settings.top_k

    def search(self, question: str) -> list[SearchHit]:
        question = question.strip()
        if not question:
            raise ValueError("A pergunta não pode estar vazia")
        query_embedding = self.embedder.embed_query(question)
        return self.vector_store.search(query_embedding, top_k=self.top_k)

    @staticmethod
    def format_context(hits: list[SearchHit]) -> str:
        sections = []
        for position, hit in enumerate(hits, start=1):
            sections.append(
                "\n".join(
                    [
                        f"[FONTE {position}]",
                        f"Documento: {hit.chunk.document}",
                        f"Página: {hit.chunk.page}",
                        f"Score: {hit.score:.4f}",
                        hit.chunk.text,
                    ]
                )
            )
        return "\n\n".join(sections)
