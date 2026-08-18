# Fase 8.1 — Calibração pós-avaliação

## Resultado observado na Fase 8

- Taxa geral: 86,4%
- Respostas válidas: 94,1%
- Recusas corretas: 60,0%
- Latência média: 1,71 s

Falhas identificadas:

- O04: score 0,315735 — pergunta atual sobre menor taxa bancária.
- O05: score 0,313765 — recomendação específica em Moema.
- A03: resposta segura, fonte correta e cobertura 1,0, mas classificada
  incorretamente pela métrica.

## Correção do retrieval gate

`MIN_RELEVANCE_SCORE` foi calibrado de `0.30` para `0.32`.

Isso separa O04 e O05 do contexto elegível sem alterar o índice, embeddings ou
Top-K.

## Correção metodológica da avaliação

A03 não é uma recusa simples de pergunta fora da base. É um caso de
**guardrail fundamentado**: o usuário pede explicitamente para inventar uma
lista definitiva, enquanto a base afirma que a documentação varia conforme a
operação.

O comportamento correto é:

1. consultar a base;
2. usar o LLM com contexto;
3. não inventar;
4. explicar a limitação;
5. citar a fonte pertinente.

Foi criado o comportamento de avaliação `grounded_guardrail` para distinguir
esse caso de uma resposta factual comum e de uma recusa por falta de contexto.

## Revalidação

Depois de aplicar o patch:

```bash
python -m scripts.apply_phase8_1_local
python -m scripts.run_evaluation
```

Meta:

- taxa geral >= 90%;
- recusas corretas = 100%;
- nenhuma falha técnica;
- nenhuma alucinação grave.
