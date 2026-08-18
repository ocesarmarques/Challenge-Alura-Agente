from __future__ import annotations
import csv, json
from pathlib import Path
from time import perf_counter

from app.agent.factory import create_production_agent
from app.evaluation.metrics import evaluate_case, summarize

ROOT_DIR = Path(__file__).resolve().parent.parent
CASES_PATH = ROOT_DIR / "evaluation" / "test_cases.json"
OUTPUT_DIR = ROOT_DIR / "evaluation" / "results"

def main():
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    agent = create_production_agent()
    results = []

    print("=== ImobIA | Avaliação formal do RAG ===")
    print(f"Casos: {len(cases)}\n")

    for i, case in enumerate(cases, 1):
        print(f"[{i:02d}/{len(cases):02d}] {case['id']} | {case['category']}")
        print(f"Pergunta: {case['question']}")
        start = perf_counter()
        try:
            answer = agent.answer(case["question"])
            latency = perf_counter() - start
            sources = [{"document": s.document, "page": s.page, "score": float(s.score)} for s in answer.sources]
            actual_names = [s["document"] for s in sources]
            score = evaluate_case(
                answer=answer.text,
                used_llm=answer.used_llm,
                actual_sources=actual_names,
                expected_behavior=case["expected_behavior"],
                expected_sources=case["expected_sources"],
                expected_keywords=case["expected_keywords"],
            )
            result = {
                **case, "answer": answer.text, "used_llm": answer.used_llm,
                "best_score": float(answer.best_score) if answer.best_score is not None else None,
                "sources": sources, "latency_seconds": round(latency, 4),
                "behavior_ok": score.behavior_ok, "source_hit": score.source_hit,
                "keyword_coverage": score.keyword_coverage, "llm_usage_ok": score.llm_usage_ok,
                "passed": score.passed, "error": None,
            }
            print(f"Resultado: {'PASSOU' if score.passed else 'FALHOU'} | LLM={answer.used_llm} | score={answer.best_score} | {latency:.2f}s\n")
        except Exception as exc:
            latency = perf_counter() - start
            result = {
                **case, "answer": "", "used_llm": None, "best_score": None,
                "sources": [], "latency_seconds": round(latency, 4),
                "behavior_ok": False, "source_hit": None, "keyword_coverage": None,
                "llm_usage_ok": False, "passed": False, "error": str(exc),
            }
            print(f"Resultado: ERRO | {exc}\n")
        results.append(result)

    summary = summarize(results)
    payload = {"summary": summary, "results": results}
    (OUTPUT_DIR / "evaluation_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = ["id","category","question","expected_behavior","passed","behavior_ok","source_hit","keyword_coverage","llm_usage_ok","used_llm","best_score","latency_seconds","actual_sources","answer","error"]
    with (OUTPUT_DIR / "evaluation_results.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow({
                "id": r["id"], "category": r["category"], "question": r["question"],
                "expected_behavior": r["expected_behavior"], "passed": r["passed"],
                "behavior_ok": r["behavior_ok"], "source_hit": r["source_hit"],
                "keyword_coverage": r["keyword_coverage"], "llm_usage_ok": r["llm_usage_ok"],
                "used_llm": r["used_llm"], "best_score": r["best_score"],
                "latency_seconds": r["latency_seconds"],
                "actual_sources": " | ".join(s["document"] for s in r["sources"]),
                "answer": r["answer"], "error": r["error"],
            })

    lines = [
        "# Relatório de Avaliação — ImobIA","",
        "## Resumo","",
        f"- Casos: **{summary['total_cases']}**",
        f"- Casos aprovados: **{summary['passed_cases']}**",
        f"- Taxa geral: **{summary['pass_rate']:.1%}**",
        f"- Respostas válidas: **{summary['answer_pass_rate']:.1%}**",
        f"- Recusas corretas: **{summary['refusal_pass_rate']:.1%}**",
        f"- Latência média: **{summary['average_latency_seconds']:.2f}s**" if summary["average_latency_seconds"] is not None else "",
        "","## Casos","",
        "| ID | Categoria | Status | LLM | Score | Tempo |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in results:
        status = "✅" if r["passed"] else "❌"
        llm = r["used_llm"] if r["used_llm"] is not None else "-"
        score = f"{r['best_score']:.3f}" if r["best_score"] is not None else "-"
        lines.append(f"| {r['id']} | {r['category']} | {status} | {llm} | {score} | {r['latency_seconds']:.2f}s |")
    failed = [r for r in results if not r["passed"]]
    lines += ["","## Casos que exigem revisão",""]
    if not failed:
        lines.append("Nenhum caso falhou na avaliação automática.")
    else:
        for r in failed:
            lines += [f"### {r['id']} — {r['question']}","",f"- Resposta: {r['answer'] or '(sem resposta)'}",f"- Erro: {r['error'] or 'nenhum'}",""]
    (OUTPUT_DIR / "evaluation_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("=" * 72)
    print("RESUMO")
    print(f"Taxa geral: {summary['pass_rate']:.1%}")
    print(f"Respostas válidas: {summary['answer_pass_rate']:.1%}")
    print(f"Recusas corretas: {summary['refusal_pass_rate']:.1%}")
    print(f"Latência média: {summary['average_latency_seconds']:.2f}s")
    print("\nArquivos gerados em evaluation/results/")

if __name__ == "__main__":
    main()
