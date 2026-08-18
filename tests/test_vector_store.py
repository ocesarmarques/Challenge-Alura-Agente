import pytest

from app.rag.chunker import Chunk
from app.rag.embeddings import HashEmbeddingProvider
from app.rag.vector_store import FaissVectorStore, NumpyVectorStore


def sample_chunks():
    return [
        Chunk("1", "financiamento.pdf", 1, "A simulação de financiamento não garante aprovação de crédito."),
        Chunk("2", "glossario.pdf", 1, "A matrícula individualiza o imóvel no cartório competente."),
        Chunk("3", "documentacao.pdf", 1, "O comprador pode apresentar documento de identificação e CPF."),
    ]


def test_numpy_vector_store_retrieval():
    embedder = HashEmbeddingProvider(dimension=128)
    chunks = sample_chunks()
    embeddings = embedder.embed_documents([c.text for c in chunks])
    store = NumpyVectorStore(embeddings, chunks)
    hits = store.search(embedder.embed_query("simulação financiamento aprovação"), top_k=1)
    assert hits[0].chunk.id == "1"


def test_faiss_vector_store_when_dependency_is_available(tmp_path):
    pytest.importorskip("faiss")
    embedder = HashEmbeddingProvider(dimension=64)
    chunks = sample_chunks()
    embeddings = embedder.embed_documents([c.text for c in chunks])
    store = FaissVectorStore.build(embeddings, chunks)
    store.save(tmp_path)
    loaded = FaissVectorStore.load(tmp_path)
    hits = loaded.search(embedder.embed_query("matrícula imóvel cartório"), top_k=1)
    assert hits[0].chunk.id == "2"
