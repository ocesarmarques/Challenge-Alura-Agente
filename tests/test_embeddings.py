import numpy as np

from app.rag.embeddings import HashEmbeddingProvider


def test_hash_embeddings_shape_and_norm():
    provider = HashEmbeddingProvider(dimension=64)
    matrix = provider.embed_documents(["financiamento imobiliário", "matrícula do imóvel"])
    assert matrix.shape == (2, 64)
    assert np.allclose(np.linalg.norm(matrix, axis=1), 1.0)


def test_hash_query_dimension():
    provider = HashEmbeddingProvider(dimension=32)
    vector = provider.embed_query("entrada financiamento")
    assert vector.shape == (32,)
