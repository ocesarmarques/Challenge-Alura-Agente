# Estratégia de testes

## Unitários

- leitura de PDFs;
- chunking;
- embeddings de teste;
- índice vetorial;
- retriever;
- prompt RAG;
- agente com contexto relevante;
- agente sem contexto relevante;
- deduplicação de fontes.

## Integração — próxima validação com credenciais OCI

1. Gerar o índice real:
   `python scripts/build_index.py`
2. Perguntar:
   `python scripts/ask.py "A simulação garante aprovação?"`
3. Validar pergunta fora da base:
   `python scripts/ask.py "Qual imóvel terá maior valorização em 2027?"`

## Categorias finais

- pergunta direta;
- paráfrase;
- combinação de informações;
- fora da base;
- tentativa de indução à alucinação.
