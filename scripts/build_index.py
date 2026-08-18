from app.config import VECTOR_STORE_DIR
from app.rag.embeddings import OCIEmbeddingProvider
from app.rag.pipeline import build_document_chunks
from app.rag.vector_store import FaissVectorStore


def main() -> None:
    print("1/4 Lendo e dividindo os PDFs...")
    pages, chunks = build_document_chunks()
    print(f"   {len(pages)} páginas -> {len(chunks)} chunks")

    print("2/4 Conectando ao OCI Generative AI...")
    embedder = OCIEmbeddingProvider()

    print("3/4 Gerando embeddings dos documentos...")
    embeddings = embedder.embed_documents([chunk.text for chunk in chunks])
    print(f"   Matriz: {embeddings.shape}")

    print("4/4 Criando e persistindo índice FAISS...")
    store = FaissVectorStore.build(embeddings=embeddings, chunks=chunks)
    store.save(VECTOR_STORE_DIR)

    print(f"Índice criado com sucesso em: {VECTOR_STORE_DIR}")


if __name__ == "__main__":
    main()
