from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.rag.retriever import Retriever
from app.rag.vector_store import SearchHit
from app.services.llm import ChatProvider


INSUFFICIENT_CONTEXT_MESSAGE = (
    "Não encontrei informação suficiente na minha base de conhecimento "
    "para responder a essa pergunta."
)


@dataclass(frozen=True)
class Source:
    document: str
    page: int
    score: float


@dataclass(frozen=True)
class AgentAnswer:
    text: str
    sources: list[Source]
    used_llm: bool
    best_score: float | None


class ImobIAAgent:
    """Orquestra recuperação semântica + geração fundamentada."""

    def __init__(
        self,
        retriever: Retriever,
        llm: ChatProvider,
        min_relevance_score: float | None = None,
    ) -> None:
        self.retriever = retriever
        self.llm = llm
        self.min_relevance_score = (
            settings.min_relevance_score
            if min_relevance_score is None
            else min_relevance_score
        )

    def _filter_hits(self, hits: list[SearchHit]) -> list[SearchHit]:
        return [
            hit
            for hit in hits
            if hit.score >= self.min_relevance_score
        ]

    @staticmethod
    def _sources_from_hits(hits: list[SearchHit]) -> list[Source]:
        unique: dict[tuple[str, int], Source] = {}

        for hit in hits:
            key = (hit.chunk.document, hit.chunk.page)

            current = unique.get(key)
            if current is None or hit.score > current.score:
                unique[key] = Source(
                    document=hit.chunk.document,
                    page=hit.chunk.page,
                    score=hit.score,
                )

        return list(unique.values())

    def answer(self, question: str) -> AgentAnswer:
        question = question.strip()

        if not question:
            raise ValueError("A pergunta não pode estar vazia.")

        hits = self.retriever.search(question)
        best_score = hits[0].score if hits else None
        relevant_hits = self._filter_hits(hits)

        if not relevant_hits:
            return AgentAnswer(
                text=INSUFFICIENT_CONTEXT_MESSAGE,
                sources=[],
                used_llm=False,
                best_score=best_score,
            )

        context = self.retriever.format_context(relevant_hits)
        answer_text = self.llm.generate(question, context)

        return AgentAnswer(
            text=answer_text,
            sources=self._sources_from_hits(relevant_hits),
            used_llm=True,
            best_score=best_score,
        )
