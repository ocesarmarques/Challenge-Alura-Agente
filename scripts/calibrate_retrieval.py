from __future__ import annotations

from app.rag.embeddings import OCIEmbeddingProvider
from app.rag.retriever import Retriever
from app.rag.vector_store import FaissVectorStore
from app.config import VECTOR_STORE_DIR


QUESTIONS = [
    ("DENTRO", "A simulação do financiamento garante aprovação?"),
    ("DENTRO", "O que é matrícula de imóvel?"),
    ("DENTRO", "Quais documentos o comprador pode precisar?"),
    ("DENTRO", "Posso utilizar FGTS na compra?"),
    ("FORA", "Qual apartamento de São Paulo valorizará mais em 2027?"),
    ("FORA", "Qual é a taxa Selic de hoje?"),
    ("FORA", "Quem ganhou o último campeonato brasileiro?"),
]


def main() -> None:
    store = FaissVectorStore.load(VECTOR_STORE_DIR)
    retriever = Retriever(store, OCIEmbeddingProvider())

    print("=== ImobIA | Calibração de recuperação ===")
    print(
        "Use estes scores para ajustar MIN_RELEVANCE_SCORE depois "
        "dos primeiros testes reais.\n"
    )

    for expected, question in QUESTIONS:
        hits = retriever.search(question)
        best = hits[0] if hits else None

        print(f"[{expected}] {question}")
        if best:
            print(
                f"  melhor score={best.score:.4f} | "
                f"{best.chunk.document} p.{best.chunk.page}"
            )
            print(f"  trecho={best.chunk.text[:180]}...")
        else:
            print("  nenhum resultado")
        print()


if __name__ == "__main__":
    main()
