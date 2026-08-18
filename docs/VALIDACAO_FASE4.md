# Validação da Fase 4

## Resultado automatizado

Execução de `pytest -q` no ambiente de construção:

- **11 testes aprovados**
- **1 teste pulado**

O teste pulado é exclusivamente o teste de persistência real do FAISS, pois a biblioteca `faiss-cpu` não está instalada no ambiente de construção. A dependência está declarada em `requirements.txt` e o teste usa `pytest.importorskip("faiss")`.

## O que foi validado

- leitura dos cinco PDFs;
- criação de chunks;
- IDs únicos;
- normalização e dimensão de embeddings de teste;
- similaridade vetorial;
- recuperação do trecho esperado;
- geração de contexto contendo documento e página;
- tratamento de parâmetros inválidos.

## O que depende do ambiente OCI do usuário

- autenticação OCI;
- chamada real ao `cohere.embed-v4.0`;
- criação do `index.faiss` com embeddings de produção;
- teste end-to-end da busca contra a OCI.

Esses pontos serão validados após configurar o tenancy/compartment e as credenciais OCI.
