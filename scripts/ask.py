import sys

from app.agent.factory import create_production_agent


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()

    if not question:
        raise SystemExit(
            'Uso: python scripts/ask.py "sua pergunta aqui"'
        )

    agent = create_production_agent()
    result = agent.answer(question)

    print("\nRESPOSTA\n")
    print(result.text)

    print("\nFONTES")
    if not result.sources:
        print("- Nenhuma fonte relevante.")
    else:
        for source in result.sources:
            print(
                f"- {source.document}, página {source.page}, "
                f"score={source.score:.4f}"
            )


if __name__ == "__main__":
    main()
