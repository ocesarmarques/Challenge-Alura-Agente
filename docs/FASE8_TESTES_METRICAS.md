# Fase 8 — Testes formais e métricas

A bateria possui 22 casos: perguntas diretas, paráfrases, combinação de contexto,
glossário, perguntas fora da base e tentativas de indução à alucinação.

## Métricas
- taxa geral de aprovação;
- taxa de respostas válidas;
- taxa de recusa correta;
- acerto de fonte;
- cobertura mínima de palavras-chave;
- latência por consulta.

## Execução
```bash
python -m scripts.run_evaluation
```

## Saídas
```text
evaluation/results/evaluation_results.json
evaluation/results/evaluation_results.csv
evaluation/results/evaluation_report.md
```

## Meta inicial
- taxa geral >= 90%;
- recusa correta = 100%;
- nenhuma alucinação grave;
- nenhuma falha técnica.
