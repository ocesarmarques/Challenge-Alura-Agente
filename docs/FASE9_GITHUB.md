# Fase 9 — GitHub e histórico de commits

## Repositório

`ocesarmarques/Challenge-Alura-Agente`

Visibilidade esperada: pública.

## Estratégia

O repositório já possuía um commit inicial criado pelo autor. A Fase 9 preserva
esse commit e publica o projeto atual em blocos funcionais, com datas reais de
publicação.

Não é feito backdating de commits.

## Segurança

Antes do commit e antes do push, o script executa:

```bash
python -m scripts.security_audit
```

Arquivos que não podem entrar no Git:

- `.env`
- `*.pem`
- `*.key`
- `.venv/`
- índice FAISS local
- resultados locais de avaliação

## Commits planejados

1. estrutura e configuração segura;
2. base documental e processamento;
3. embeddings, FAISS e agente RAG;
4. interface Streamlit;
5. testes e avaliação formal;
6. OCI, validações e utilitários;
7. README atual.

Essa sequência descreve blocos funcionais do estado atual do projeto e não
pretende simular datas passadas.

## Publicação

A partir da pasta do ImobIA:

```bash
bash scripts/publish_github.sh
```

O script clona o repositório já existente para
`~/Downloads/Challenge-Alura-Agente`, sincroniza os arquivos, cria commits
somente quando há alterações, audita segredos e envia a branch `main`.
