import argparse

from app.config import VECTOR_STORE_DIR
from app.rag.embeddings import OCIEmbeddingProvider
from app.rag.retriever import Retriever
from app.rag.vector_store import FaissVectorStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca semântica na base do ImobIA")
    parser.add_argument("question", help="Pergunta em linguagem natural")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    store = FaissVectorStore.load(VECTOR_STORE_DIR)
    embedder = OCIEmbeddingProvider()
    retriever = Retriever(store, embedder, top_k=args.top_k)

    hits = retriever.search(args.question)
    print(retriever.format_context(hits))


if __name__ == "__main__":
    main()
