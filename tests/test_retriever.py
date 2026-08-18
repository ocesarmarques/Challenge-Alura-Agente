from app.rag.chunker import Chunk
from app.rag.embeddings import HashEmbeddingProvider
from app.rag.retriever import Retriever
from app.rag.vector_store import NumpyVectorStore


def build_retriever():
    chunks = [
        Chunk("1", "financiamento.pdf", 2, "A simulação não representa aprovação definitiva do financiamento."),
        Chunk("2", "glossario.pdf", 1, "Matrícula é o registro que individualiza o imóvel."),
    ]
    embedder = HashEmbeddingProvider(dimension=96)
    embeddings = embedder.embed_documents([c.text for c in chunks])
    store = NumpyVectorStore(embeddings, chunks)
    return Retriever(store, embedder, top_k=1)


def test_retriever_returns_relevant_chunk():
    retriever = build_retriever()
    hits = retriever.search("simulação é aprovação definitiva?")
    assert hits[0].chunk.id == "1"


def test_context_contains_source_metadata():
    retriever = build_retriever()
    context = retriever.format_context(retriever.search("matrícula imóvel"))
    assert "Documento:" in context
    assert "Página:" in context
    assert "glossario.pdf" in context
