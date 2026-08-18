from app.evaluation.metrics import (
    evaluate_case,
    keyword_coverage,
    source_hit,
    summarize,
)

def test_keyword_coverage():
    assert keyword_coverage(
        "A simulação não garante aprovação.",
        ["simulação", "não", "aprovação"],
    ) == 1.0

def test_source_hit():
    assert source_hit(
        ["faq.pdf", "guia.pdf"],
        ["faq.pdf"],
    ) is True

def test_answer_case_passes():
    score = evaluate_case(
        answer="Não. A simulação não garante aprovação.",
        used_llm=True,
        actual_sources=["faq.pdf"],
        expected_behavior="answer",
        expected_sources=["faq.pdf"],
        expected_keywords=["simulação", "não", "aprovação"],
    )
    assert score.passed is True

def test_refusal_requires_llm_skipped():
    score = evaluate_case(
        answer=(
            "Não encontrei informação suficiente na minha base de "
            "conhecimento para responder a essa pergunta."
        ),
        used_llm=False,
        actual_sources=[],
        expected_behavior="refuse",
        expected_sources=[],
        expected_keywords=[],
    )
    assert score.passed is True

def test_refusal_fails_if_llm_used():
    score = evaluate_case(
        answer=(
            "Não encontrei informação suficiente na minha base de "
            "conhecimento para responder a essa pergunta."
        ),
        used_llm=True,
        actual_sources=[],
        expected_behavior="refuse",
        expected_sources=[],
        expected_keywords=[],
    )
    assert score.passed is False

def test_grounded_guardrail_allows_explicit_limitation():
    score = evaluate_case(
        answer=(
            "Não encontrei informação suficiente na minha base de "
            "conhecimento para fornecer uma lista completa e definitiva. "
            "A documentação varia conforme a operação."
        ),
        used_llm=True,
        actual_sources=["02_documentacao_imovel.pdf"],
        expected_behavior="grounded_guardrail",
        expected_sources=["02_documentacao_imovel.pdf"],
        expected_keywords=["varia", "operação"],
    )
    assert score.passed is True

def test_grounded_guardrail_still_requires_source():
    score = evaluate_case(
        answer="A documentação varia conforme a operação.",
        used_llm=True,
        actual_sources=[],
        expected_behavior="grounded_guardrail",
        expected_sources=["02_documentacao_imovel.pdf"],
        expected_keywords=["varia", "operação"],
    )
    assert score.passed is False

def test_unknown_behavior_raises():
    try:
        evaluate_case(
            answer="x",
            used_llm=True,
            actual_sources=[],
            expected_behavior="desconhecido",
            expected_sources=[],
            expected_keywords=[],
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Era esperado ValueError.")

def test_summary_counts_guardrail_as_answer_like():
    summary = summarize([
        {
            "passed": True,
            "expected_behavior": "answer",
            "latency_seconds": 1.0,
        },
        {
            "passed": True,
            "expected_behavior": "grounded_guardrail",
            "latency_seconds": 1.2,
        },
        {
            "passed": True,
            "expected_behavior": "refuse",
            "latency_seconds": 0.5,
        },
    ])

    assert summary["total_cases"] == 3
    assert summary["answer_cases"] == 2
    assert summary["answer_pass_rate"] == 1.0
    assert summary["refusal_cases"] == 1
    assert summary["refusal_pass_rate"] == 1.0
