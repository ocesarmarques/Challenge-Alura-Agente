from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from app.config import VECTOR_STORE_DIR, settings
from app.rag.pipeline import build_document_chunks
from app.ui.components import (
    SUGGESTED_QUESTIONS,
    answer_to_message,
    clear_conversation,
    document_label,
    init_session_state,
    render_assistant_message,
    render_user_message,
    set_pending_question,
)


st.set_page_config(
    page_title=f"{settings.app_title} | Atendimento Imobiliário",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .block-container {
        max-width: 1050px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    .imobia-hero {
        padding: 1.35rem 1.5rem;
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 18px;
        margin-bottom: 1rem;
    }
    .imobia-kicker {
        font-size: .8rem;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
        opacity: .68;
        margin-bottom: .3rem;
    }
    .imobia-title {
        font-size: 2.15rem;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: .45rem;
    }
    .imobia-subtitle {
        font-size: 1.02rem;
        opacity: .78;
        max-width: 760px;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_base_summary():
    pages, chunks = build_document_chunks()
    documents = sorted({page.document for page in pages})
    return documents, len(pages), len(chunks)


@st.cache_resource(show_spinner=False)
def get_agent():
    from app.agent.factory import create_production_agent
    return create_production_agent()


def render_sidebar(
    document_names: list[str],
    page_count: int,
    chunk_count: int,
    index_ready: bool,
) -> None:
    with st.sidebar:
        st.markdown("## 🏠 ImobIA")
        st.caption("Challenge Alura Agente")

        if index_ready:
            st.success("RAG disponível", icon="✅")
        else:
            st.warning("Índice vetorial ausente", icon="⚠️")

        col1, col2 = st.columns(2)
        col1.metric("PDFs", len(document_names))
        col2.metric("Chunks", chunk_count)
        st.caption(f"{page_count} páginas processadas")

        st.divider()
        st.markdown("### 💡 Experimente perguntar")

        for number, question in enumerate(SUGGESTED_QUESTIONS):
            st.button(
                question,
                key=f"suggestion_{number}",
                use_container_width=True,
                disabled=not index_ready,
                on_click=set_pending_question,
                args=(question,),
            )

        st.divider()

        with st.expander("📚 Base de conhecimento"):
            for document in document_names:
                st.markdown(f"• {document_label(document)}")

        with st.expander("🧠 Como funciona"):
            st.markdown(
                """
                **1.** Sua pergunta vira um embedding.  
                **2.** O FAISS localiza trechos semanticamente relevantes.  
                **3.** O contexto recuperado é enviado ao modelo da OCI.  
                **4.** A resposta é apresentada com as fontes usadas.
                """
            )

        if st.button(
            "🗑️ Nova conversa",
            use_container_width=True,
            on_click=clear_conversation,
        ):
            pass

        st.caption(
            "Conteúdo educacional. O ImobIA não substitui orientação "
            "jurídica, financeira ou imobiliária profissional."
        )


def render_empty_state():
    st.markdown("### Como posso ajudar?")
    st.write(
        "Faça uma pergunta sobre compra de imóveis, documentação, "
        "financiamento, FGTS ou termos imobiliários."
    )

    st.info(
        "O ImobIA responde com base nos PDFs do projeto. "
        "Se a informação não estiver na base, ele informa a limitação "
        "em vez de inventar uma resposta.",
        icon="🛡️",
    )


def process_question(question: str) -> None:
    question = question.strip()
    if not question:
        return

    user_message = {
        "role": "user",
        "content": question,
    }
    st.session_state.messages.append(user_message)

    render_user_message(user_message)

    try:
        with st.chat_message("assistant", avatar="🏠"):
            with st.spinner("Consultando a base de conhecimento..."):
                result = get_agent().answer(question)

            assistant_message = answer_to_message(result)
            st.markdown(assistant_message["content"])

            from app.ui.components import render_sources
            render_sources(assistant_message["sources"])

            if not result.used_llm:
                st.caption(
                    "Resposta interrompida antes do LLM porque nenhum trecho "
                    "atingiu o limiar mínimo de relevância."
                )

        st.session_state.messages.append(assistant_message)

    except Exception as exc:
        st.error(
            "Não foi possível concluir a consulta. "
            "Verifique a conexão e a configuração da OCI."
        )
        with st.expander("Detalhes técnicos"):
            st.code(str(exc))


init_session_state()

try:
    document_names, page_count, chunk_count = load_base_summary()
except Exception as exc:
    st.error(f"Não foi possível carregar a base documental: {exc}")
    st.stop()

index_path = Path(VECTOR_STORE_DIR) / "index.faiss"
metadata_path = Path(VECTOR_STORE_DIR) / "metadata.json"
index_ready = index_path.exists() and metadata_path.exists()

render_sidebar(
    document_names=document_names,
    page_count=page_count,
    chunk_count=chunk_count,
    index_ready=index_ready,
)

st.markdown(
    """
    <div class="imobia-hero">
      <div class="imobia-kicker">Inteligência artificial + RAG</div>
      <div class="imobia-title">🏠 ImobIA</div>
      <div class="imobia-subtitle">
        Um agente inteligente que consulta uma base documental imobiliária
        antes de responder — com transparência sobre as fontes utilizadas.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not index_ready:
    st.warning(
        "O índice vetorial ainda não está disponível neste ambiente. "
        "Execute `python -m scripts.build_index` antes de conversar com o agente.",
        icon="⚠️",
    )

if not st.session_state.messages:
    render_empty_state()

for message in st.session_state.messages:
    if message["role"] == "user":
        render_user_message(message)
    else:
        render_assistant_message(message)

pending_question = st.session_state.pending_question
st.session_state.pending_question = None

typed_question = st.chat_input(
    "Pergunte ao ImobIA...",
    disabled=not index_ready,
)

question = typed_question or pending_question

if question:
    process_question(question)

st.caption(
    "ImobIA • Challenge Alura Agente • Respostas fundamentadas em documentos PDF"
)
