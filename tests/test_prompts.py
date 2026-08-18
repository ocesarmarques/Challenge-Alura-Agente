from app.agent.prompts import SYSTEM_PROMPT, build_rag_prompt


def test_system_prompt_contains_grounding_rule():
    assert "Não invente" in SYSTEM_PROMPT
    assert "base de conhecimento" in SYSTEM_PROMPT


def test_rag_prompt_contains_question_and_context():
    prompt = build_rag_prompt(
        "O que é matrícula?",
        "Matrícula é um registro do imóvel.",
    )

    assert "O que é matrícula?" in prompt
    assert "Matrícula é um registro" in prompt
    assert "<CONTEXTO>" in prompt
