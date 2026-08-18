from app.agent.agent import AgentAnswer, Source
from app.ui.components import (
    answer_to_message,
    document_label,
    source_to_dict,
)


def test_document_label_known_file():
    assert (
        document_label("03_financiamento_imobiliario.pdf")
        == "Guia de Financiamento Imobiliário"
    )


def test_document_label_fallback():
    assert document_label("arquivo_teste.pdf") == "Arquivo Teste"


def test_source_to_dict():
    source = Source(
        document="faq.pdf",
        page=2,
        score=0.71,
    )

    data = source_to_dict(source)

    assert data["document"] == "faq.pdf"
    assert data["page"] == 2
    assert data["score"] == 0.71


def test_answer_to_message_preserves_sources_and_metadata():
    result = AgentAnswer(
        text="Resposta.",
        sources=[
            Source(
                document="faq.pdf",
                page=1,
                score=0.8,
            )
        ],
        used_llm=True,
        best_score=0.8,
    )

    message = answer_to_message(result)

    assert message["role"] == "assistant"
    assert message["content"] == "Resposta."
    assert message["used_llm"] is True
    assert message["sources"][0]["document"] == "faq.pdf"
