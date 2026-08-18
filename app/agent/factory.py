from app.agent.agent import ImobIAAgent
from app.config import VECTOR_STORE_DIR
from app.rag.embeddings import OCIEmbeddingProvider
from app.rag.retriever import Retriever
from app.rag.vector_store import FaissVectorStore
from app.services.llm import OCIChatProvider


def create_production_agent() -> ImobIAAgent:
    store = FaissVectorStore.load(VECTOR_STORE_DIR)
    embedder = OCIEmbeddingProvider()
    retriever = Retriever(store, embedder)
    llm = OCIChatProvider()

    return ImobIAAgent(
        retriever=retriever,
        llm=llm,
    )
