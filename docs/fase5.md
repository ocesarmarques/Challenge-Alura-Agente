# Fase 5 — RAG completo

## Objetivo

Conectar a recuperação semântica da Fase 4 ao modelo generativo da OCI.

## Fluxo

```text
Pergunta
  ↓
Embedding SEARCH_QUERY
  ↓
FAISS
  ↓
Top-K chunks
  ↓
Filtro de relevância
  ↓
Contexto
  ↓
Cohere Command A / OCI Generative AI
  ↓
Resposta
  ↓
Fontes (documento + página)
```

## Modelo de chat

Padrão do projeto:

`cohere.command-a-03-2025`

## Controle contra alucinação

O projeto possui duas camadas:

1. **Filtro de relevância:** se nenhum trecho atingir
   `MIN_RELEVANCE_SCORE`, o LLM nem é chamado.
2. **Prompt de grounding:** o modelo é instruído a usar apenas o contexto
   fornecido e informar insuficiência quando a base não sustentar a resposta.

O limiar é configurável e deverá ser calibrado com embeddings reais durante os
testes integrados.

## Fontes

As referências exibidas ao usuário vêm dos metadados preservados no pipeline,
e não são inventadas pelo LLM.
