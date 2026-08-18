from app.agent.agent import (
    INSUFFICIENT_CONTEXT_MESSAGE,
    ImobIAAgent,
)
from app.rag.chunker import Chunk
from app.rag.vector_store import SearchHit
from app.services.llm import StaticChatProvider


class FakeRetriever:
    def __init__(self, hits):
        self.hits = hits
        self.questions = []

    def search(self, question):
        self.questions.append(question)
        return self.hits

    @staticmethod
    def format_context(hits):
        return "\n".join(
            f"{h.chunk.document} p.{h.chunk.page}: {h.chunk.text}"
            for h in hits
        )


def hit(score, document="base.pdf", page=1, text="Conteúdo relevante"):
    return SearchHit(
        chunk=Chunk(
            id=f"{document}:{page}:{score}",
            document=document,
            page=page,
            text=text,
        ),
        score=score,
    )


def test_agent_generates_answer_when_context_is_relevant():
    retriever = FakeRetriever([
        hit(0.82, "financiamento.pdf", 2, "Simulação não garante aprovação.")
    ])
    llm = StaticChatProvider("Não. A simulação não garante aprovação.")
    agent = ImobIAAgent(retriever, llm, min_relevance_score=0.20)

    result = agent.answer("A simulação garante aprovação?")

    assert result.used_llm is True
    assert "não garante" in result.text.lower()
    assert len(llm.calls) == 1
    assert result.sources[0].document == "financiamento.pdf"
    assert result.sources[0].page == 2


def test_agent_skips_llm_when_context_is_weak():
    retriever = FakeRetriever([
        hit(0.08, "glossario.pdf", 1, "Texto não relacionado.")
    ])
    llm = StaticChatProvider("Não deveria ser chamada.")
    agent = ImobIAAgent(retriever, llm, min_relevance_score=0.20)

    result = agent.answer("Qual imóvel valorizará mais em 2027?")

    assert result.text == INSUFFICIENT_CONTEXT_MESSAGE
    assert result.used_llm is False
    assert result.sources == []
    assert llm.calls == []


def test_sources_are_deduplicated_by_document_and_page():
    retriever = FakeRetriever([
        hit(0.90, "faq.pdf", 1, "Trecho A"),
        hit(0.80, "faq.pdf", 1, "Trecho B"),
        hit(0.70, "guia.pdf", 2, "Trecho C"),
    ])
    llm = StaticChatProvider("Resposta.")
    agent = ImobIAAgent(retriever, llm, min_relevance_score=0.20)

    result = agent.answer("Pergunta")

    assert len(result.sources) == 2
    assert result.sources[0].document == "faq.pdf"
    assert result.sources[0].score == 0.90


def test_empty_question_raises_value_error():
    retriever = FakeRetriever([])
    llm = StaticChatProvider()
    agent = ImobIAAgent(retriever, llm)

    try:
        agent.answer("   ")
        assert False, "Era esperado ValueError"
    except ValueError:
        pass
