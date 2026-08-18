# Fase 4 — Embeddings, FAISS e Recuperação Semântica

## Objetivo

Transformar os chunks dos PDFs em vetores, armazená-los em um índice FAISS e recuperar os trechos mais relacionados à pergunta do usuário.

## Fluxo

```text
PDFs
 ↓
Chunks + metadados
 ↓
OCI Cohere Embed 4
 input_type=SEARCH_DOCUMENT
 ↓
Embeddings normalizados
 ↓
FAISS IndexFlatIP
 ↓
Pergunta
 ↓
OCI Cohere Embed 4
 input_type=SEARCH_QUERY
 ↓
Busca por similaridade cosseno
 ↓
Top-K chunks + documento + página
```

## Modelo

Produção: `cohere.embed-v4.0`, configurado para 1024 dimensões.

O modelo é configurável por variáveis de ambiente; uma troca de dimensão exige recriar o índice.

## Persistência

A pasta `data/vector_store/` recebe:

- `index.faiss`: índice vetorial;
- `metadata.json`: chunks, documentos e páginas.

Esses arquivos são gerados e não entram no Git por padrão.

## Testes sem consumo de API

`HashEmbeddingProvider` existe apenas para testes automatizados do pipeline. Ele não substitui o modelo da OCI em produção.

## Comandos

Criar o índice com OCI:

```bash
python scripts/build_index.py
```

Testar busca semântica:

```bash
python scripts/search_demo.py "A simulação garante que meu financiamento foi aprovado?"
```
