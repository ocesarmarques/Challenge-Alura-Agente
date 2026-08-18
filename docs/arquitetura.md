# Arquitetura do ImobIA

## Pipeline completo até a Fase 5

```text
PDFs
 ↓
PyMuPDF
 ↓
Texto por página
 ↓
Chunking + metadados
 ↓
Cohere Embed 4 / OCI
 ↓
FAISS
 ↓
Retriever semântico
 ↓
Filtro de relevância
 ↓
Contexto recuperado
 ↓
Cohere Command A / OCI
 ↓
Resposta fundamentada
 ↓
Fontes: documento + página
```

## Componentes

- `app/rag/loader.py`: leitura dos PDFs.
- `app/rag/chunker.py`: divisão do texto.
- `app/rag/embeddings.py`: embeddings OCI.
- `app/rag/vector_store.py`: persistência e busca FAISS.
- `app/rag/retriever.py`: recuperação de trechos.
- `app/services/llm.py`: geração via OCI Generative AI.
- `app/agent/agent.py`: orquestra o RAG.
- `app/agent/factory.py`: monta dependências de produção.
- `app/main.py`: interface Streamlit.
