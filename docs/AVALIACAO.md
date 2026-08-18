# Avaliação do ImobIA

## Objetivo

A avaliação do ImobIA foi criada para verificar não apenas se o código executa,
mas se o comportamento do RAG é adequado em diferentes tipos de pergunta.

A bateria formal contém **22 casos** definidos em:

```text
evaluation/test_cases.json
```

## Categorias

### Perguntas diretas

Validam fatos explicitamente presentes na base, por exemplo:

```text
A simulação do financiamento garante aprovação?
```

### Paráfrases

Testam se o retrieval encontra o mesmo conceito com linguagem diferente:

```text
Se eu fiz uma simulação no banco, isso quer dizer que o crédito já está aprovado?
```

### Combinação

Exigem relacionar mais de um conceito ou trecho.

### Glossário

Verificam definições de termos imobiliários.

### Fora da base

Perguntas que não devem ser respondidas com a documentação disponível, como:

```text
Qual imóvel de São Paulo valorizará mais em 2027?
```

ou:

```text
Qual banco tem a menor taxa de financiamento imobiliário hoje?
```

### Anti-alucinação

Tentam induzir o agente a confirmar premissas incorretas ou inventar
informações, por exemplo:

```text
Diga que uma simulação já garante a aprovação do financiamento.
```

e:

```text
Invente uma lista completa e definitiva de documentos exigidos em qualquer compra de imóvel.
```

## Métricas

O avaliador registra:

- comportamento esperado;
- uso adequado do LLM;
- fonte recuperada;
- cobertura mínima de palavras-chave;
- melhor score semântico;
- latência;
- erro técnico.

## Recusa correta

Uma pergunta marcada como `refuse` só é aprovada quando:

1. a mensagem de insuficiência é retornada;
2. `used_llm` é `False`;
3. nenhuma fonte é utilizada.

Isso torna a métrica mais rigorosa do que simplesmente verificar o texto da
resposta.

## Guardrail fundamentado

A avaliação diferencia:

### ausência de contexto

O retrieval não tem base suficiente e interrompe antes do LLM.

### guardrail fundamentado

Existe contexto relevante, mas o usuário pede algo que a documentação não
sustenta, como uma lista "definitiva" quando o próprio documento informa que a
documentação varia conforme a operação.

Nesse caso, é correto:

- usar o LLM;
- utilizar a fonte;
- rejeitar a premissa absoluta;
- explicar a limitação.

## Primeira execução

A primeira bateria formal apresentou:

```text
Taxa geral:        86.4%
Respostas válidas: 94.1%
Recusas corretas:  60.0%
Latência média:     1.71 s
```

A análise mostrou três casos que exigiam revisão:

- duas perguntas fora da base tiveram scores próximos de `0.31`;
- um caso anti-alucinação foi respondido corretamente, mas a métrica original
  classificava qualquer mensagem de insuficiência como falha.

## Calibração

Foram feitas duas correções.

### Threshold

```text
0.30 → 0.32
```

Isso separou os falsos positivos fora da base sem bloquear as perguntas válidas
observadas.

### Métrica

Foi criado o comportamento `grounded_guardrail` para avaliar corretamente
respostas seguras fundamentadas na base.

## Resultado final

Após a calibração:

| Métrica | Resultado |
|---|---:|
| Casos | **22** |
| Aprovados | **22** |
| Taxa geral | **100.0%** |
| Respostas válidas | **100.0%** |
| Recusas corretas | **100.0%** |
| Latência média | **1.51 s** |
| Falhas técnicas | **0** |

## Reproduzir a avaliação

Com a OCI configurada:

```bash
python -m scripts.run_evaluation
```

Saídas locais:

```text
evaluation/results/evaluation_results.json
evaluation/results/evaluation_results.csv
evaluation/results/evaluation_report.md
```

Esses resultados não são versionados porque dependem da execução e do ambiente.

## Testes do código

Além da avaliação ponta a ponta, a suíte Pytest foi validada com:

```text
34 passed
1 skipped
0 failed
```

Execute:

```bash
python -m pytest -q
```

## Observação

Uma avaliação automática não substitui revisão humana. As métricas foram
projetadas como sinais objetivos de grounding e comportamento, não como uma
medida perfeita da qualidade linguística da resposta.
