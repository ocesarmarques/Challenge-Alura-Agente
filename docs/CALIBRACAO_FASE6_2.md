# Fase 6.2 — Calibração de relevância e PyMuPDF

## Scores observados

Perguntas dentro da base:
- 0.5151
- 0.5391
- 0.5828
- 0.5728

Perguntas fora da base:
- 0.1588
- 0.0971
- 0.1286

Em um smoke test anterior, uma pergunta fora da base chegou a 0.2097.

## Decisão

`MIN_RELEVANCE_SCORE=0.30`

Esse valor mantém uma margem confortável entre os exemplos válidos e os
exemplos claramente fora da base.

## PyMuPDF

O import legado `fitz` foi substituído por:

```python
import pymupdf
```

para evitar o aviso de depreciação.

## Aplicação local

Depois de atualizar os arquivos:

```bash
./scripts/apply_phase6_2_local.sh
python -m scripts.phase6_smoke_test
```

O caso fora da base deve idealmente mostrar:

```text
LLM usado: False
```
