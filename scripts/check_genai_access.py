from __future__ import annotations

from app.rag.embeddings import OCIEmbeddingProvider
from app.services.llm import OCIChatProvider


def main() -> int:
    print("=== ImobIA | Verificação OCI Generative AI ===")

    try:
        print("1/2 Testando embeddings...")
        embedder = OCIEmbeddingProvider()
        vector = embedder.embed_query(
            "Teste de conectividade do projeto ImobIA."
        )
        print(f"[OK] Embedding retornado com dimensão {len(vector)}.")
    except Exception as exc:
        print(f"[ERRO] Embeddings OCI: {exc}")
        return 1

    try:
        print("2/2 Testando chat...")
        llm = OCIChatProvider()
        answer = llm.generate(
            question="O que é uma matrícula de imóvel?",
            context=(
                "Documento: glossario.pdf\n"
                "Página: 1\n"
                "Matrícula é o registro que individualiza o imóvel "
                "no cartório competente."
            ),
        )
        print("[OK] Chat OCI respondeu.")
        print(f"Resposta de teste: {answer}")
    except Exception as exc:
        print(f"[ERRO] Chat OCI: {exc}")
        return 1

    print("RESULTADO: acesso ao OCI Generative AI validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
