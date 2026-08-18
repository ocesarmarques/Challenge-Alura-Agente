from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from app.agent.agent import AgentAnswer, Source


DOCUMENT_LABELS = {
    "01_guia_compra_imovel.pdf": "Guia de Compra de Imóveis",
    "02_documentacao_imovel.pdf": "Documentação para Compra de Imóveis",
    "03_financiamento_imobiliario.pdf": "Guia de Financiamento Imobiliário",
    "04_faq_imobiliario.pdf": "FAQ Imobiliário",
    "05_glossario_imobiliario.pdf": "Glossário Imobiliário",
}

SUGGESTED_QUESTIONS = [
    "A simulação do financiamento garante aprovação?",
    "Quais documentos o comprador pode precisar apresentar?",
    "Posso utilizar FGTS na compra de um imóvel?",
    "O que é matrícula de imóvel?",
]


def document_label(filename: str) -> str:
    return DOCUMENT_LABELS.get(
        filename,
        Path(filename).stem.replace("_", " ").title(),
    )


def source_to_dict(source: Source) -> dict:
    return asdict(source)


def answer_to_message(result: AgentAnswer) -> dict:
    return {
        "role": "assistant",
        "content": result.text,
        "sources": [source_to_dict(source) for source in result.sources],
        "used_llm": result.used_llm,
        "best_score": result.best_score,
    }


def render_sources(sources: list[dict] | list[Source]) -> None:
    import streamlit as st

    if not sources:
        st.caption("Nenhuma fonte da base foi utilizada nesta resposta.")
        return

    with st.expander(
        f"📚 Fontes consultadas ({len(sources)})",
        expanded=False,
    ):
        for index, source in enumerate(sources, start=1):
            if isinstance(source, dict):
                document = source["document"]
                page = source["page"]
                score = source.get("score")
            else:
                document = source.document
                page = source.page
                score = source.score

            st.markdown(
                f"**{index}. {document_label(document)}**  \n"
                f"`{document}` · página **{page}**"
            )
            if score is not None:
                st.caption(
                    f"Relevância semântica: {float(score):.3f}"
                )


def render_assistant_message(message: dict) -> None:
    import streamlit as st

    with st.chat_message("assistant", avatar="🏠"):
        st.markdown(message["content"])
        render_sources(message.get("sources", []))


def render_user_message(message: dict) -> None:
    import streamlit as st

    with st.chat_message("user"):
        st.markdown(message["content"])


def init_session_state() -> None:
    import streamlit as st

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None


def clear_conversation() -> None:
    import streamlit as st

    st.session_state.messages = []
    st.session_state.pending_question = None


def set_pending_question(question: str) -> None:
    import streamlit as st

    st.session_state.pending_question = question
