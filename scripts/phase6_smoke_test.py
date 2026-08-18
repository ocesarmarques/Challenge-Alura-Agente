from __future__ import annotations

from pathlib import Path

from app.agent.factory import create_production_agent
from app.config import VECTOR_STORE_DIR
from app.rag.embeddings import OCIEmbeddingProvider
from app.rag.pipeline import build_document_chunks
from app.rag.vector_store import FaissVectorStore


KNOWN_QUESTION = "A simulação do financiamento garante aprovação?"
OUT_OF_BASE_QUESTION = "Qual imóvel de São Paulo valorizará mais em 2027?"


def ensure_index() -> None:
    index_file = Path(VECTOR_STORE_DIR) / "index.faiss"
    metadata_file = Path(VECTOR_STORE_DIR) / "metadata.json"

    if index_file.exists() and metadata_file.exists():
        print("[OK] Índice FAISS já existe.")
        return

    print("Índice ainda não existe. Gerando...")
    _, chunks = build_document_chunks()
    embedder = OCIEmbeddingProvider()
    embeddings = embedder.embed_documents([chunk.text for chunk in chunks])

    store = FaissVectorStore.build(embeddings, chunks)
    store.save(VECTOR_STORE_DIR)
    print("[OK] Índice gerado.")


def ask(agent, question: str) -> None:
    print("\n" + "=" * 70)
    print(f"PERGUNTA: {question}")
    result = agent.answer(question)
    print(f"\nRESPOSTA:\n{result.text}")
    print(f"\nLLM usado: {result.used_llm}")
    print(f"Melhor score: {result.best_score}")

    print("\nFONTES:")
    if result.sources:
        for source in result.sources:
            print(
                f"- {source.document}, página {source.page}, "
                f"score={source.score:.4f}"
            )
    else:
        print("- nenhuma")


def main() -> None:
    print("=== ImobIA | Smoke test ponta a ponta ===")
    ensure_index()
    agent = create_production_agent()

    ask(agent, KNOWN_QUESTION)
    ask(agent, OUT_OF_BASE_QUESTION)

    print("\nSmoke test concluído.")
    print(
        "Revise os resultados e, se necessário, execute "
        "python scripts/calibrate_retrieval.py."
    )


if __name__ == "__main__":
    main()
