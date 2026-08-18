from __future__ import annotations
from dataclasses import dataclass

INSUFFICIENT_MARKER = (
    "não encontrei informação suficiente na minha base de conhecimento"
)

@dataclass(frozen=True)
class CaseScore:
    behavior_ok: bool
    source_hit: bool | None
    keyword_coverage: float | None
    llm_usage_ok: bool
    passed: bool

def normalize(text: str) -> str:
    return " ".join(text.lower().split())

def keyword_coverage(answer: str, keywords: list[str]) -> float | None:
    if not keywords:
        return None
    normalized_answer = normalize(answer)
    hits = sum(
        1 for keyword in keywords
        if normalize(keyword) in normalized_answer
    )
    return hits / len(keywords)

def source_hit(
    actual_sources: list[str],
    expected_sources: list[str],
) -> bool | None:
    if not expected_sources:
        return None
    return bool(set(actual_sources).intersection(expected_sources))

def evaluate_case(
    *,
    answer: str,
    used_llm: bool,
    actual_sources: list[str],
    expected_behavior: str,
    expected_sources: list[str],
    expected_keywords: list[str],
    min_keyword_coverage: float = 0.50,
) -> CaseScore:
    normalized = normalize(answer)

    if expected_behavior == "refuse":
        behavior_ok = INSUFFICIENT_MARKER in normalized
        llm_usage_ok = used_llm is False
        passed = behavior_ok and llm_usage_ok and not actual_sources
        return CaseScore(
            behavior_ok,
            None,
            None,
            llm_usage_ok,
            passed,
        )

    source_ok = source_hit(actual_sources, expected_sources)
    coverage = keyword_coverage(answer, expected_keywords)
    llm_usage_ok = used_llm is True

    if expected_behavior == "grounded_guardrail":
        # A guardrail answer may explicitly say that the requested certainty
        # is unavailable, provided it uses the KB and explains the limitation.
        behavior_ok = bool(answer.strip())
        passed = (
            behavior_ok
            and llm_usage_ok
            and (source_ok is not False)
            and (
                coverage is None
                or coverage >= min_keyword_coverage
            )
        )
        return CaseScore(
            behavior_ok,
            source_ok,
            coverage,
            llm_usage_ok,
            passed,
        )

    if expected_behavior != "answer":
        raise ValueError(
            f"Comportamento esperado desconhecido: {expected_behavior}"
        )

    behavior_ok = INSUFFICIENT_MARKER not in normalized
    passed = (
        behavior_ok
        and llm_usage_ok
        and (source_ok is not False)
        and (
            coverage is None
            or coverage >= min_keyword_coverage
        )
    )

    return CaseScore(
        behavior_ok,
        source_ok,
        coverage,
        llm_usage_ok,
        passed,
    )

def summarize(results: list[dict]) -> dict:
    total = len(results)
    passed = sum(bool(r["passed"]) for r in results)

    answer_like = [
        r for r in results
        if r["expected_behavior"] != "refuse"
    ]
    refusals = [
        r for r in results
        if r["expected_behavior"] == "refuse"
    ]

    latencies = [
        float(r["latency_seconds"])
        for r in results
        if r.get("latency_seconds") is not None
    ]

    return {
        "total_cases": total,
        "passed_cases": passed,
        "pass_rate": passed / total if total else 0.0,
        "answer_cases": len(answer_like),
        "answer_pass_rate": (
            sum(bool(r["passed"]) for r in answer_like)
            / len(answer_like)
            if answer_like else 0.0
        ),
        "refusal_cases": len(refusals),
        "refusal_pass_rate": (
            sum(bool(r["passed"]) for r in refusals)
            / len(refusals)
            if refusals else 0.0
        ),
        "average_latency_seconds": (
            sum(latencies) / len(latencies)
            if latencies else None
        ),
        "max_latency_seconds": (
            max(latencies) if latencies else None
        ),
    }
