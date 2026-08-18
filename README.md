# 🏠 ImobIA — Agente Inteligente de Atendimento Imobiliário

Projeto desenvolvido para o **Challenge Alura Agente**.

O ImobIA usa **RAG (Retrieval-Augmented Generation)** para responder perguntas
sobre compra de imóveis com base em uma coleção de documentos PDF.

## Status

✅ Fase 5 implementada: pipeline RAG completo em código.

A validação integrada com a tenancy OCI será feita após a configuração das
credenciais e geração do índice vetorial real.

## Fluxo

```text
Usuário
 ↓
Streamlit
 ↓
Pergunta
 ↓
Cohere Embed 4 (OCI)
 ↓
FAISS
 ↓
Trechos relevantes dos PDFs
 ↓
Filtro de relevância
 ↓
Cohere Command A (OCI)
 ↓
Resposta fundamentada
 ↓
Fontes: documento + página
```

## Base de conhecimento

1. Guia de Compra de Imóveis
2. Documentação para Compra de Imóveis
3. Guia de Financiamento Imobiliário
4. FAQ Imobiliário
5. Glossário Imobiliário

## Tecnologias

- Python
- Streamlit
- PyMuPDF
- NumPy
- FAISS
- OCI Python SDK
- OCI Generative AI
- Cohere Embed 4
- Cohere Command A
- Pytest
- Docker

## Modelos padrão

- Embeddings: `cohere.embed-v4.0`
- Chat: `cohere.command-a-03-2025`

## Configuração

Copie:

```bash
cp .env.example .env
```

Preencha `OCI_COMPARTMENT_ID` e configure o arquivo `~/.oci/config`.

## Criar o índice vetorial

```bash
python scripts/build_index.py
```

## Teste completo pelo terminal

```bash
python scripts/ask.py "A simulação garante aprovação do financiamento?"
```

## Executar interface

```bash
streamlit run app/main.py
```

## Tratamento de perguntas fora da base

Se nenhum trecho atingir o limiar de relevância configurado, o modelo
generativo não é chamado e o agente informa que não encontrou informação
suficiente na base.

Além disso, o prompt do LLM proíbe preencher lacunas com conhecimento externo.

## Aviso

A documentação imobiliária utilizada no projeto é fictícia e educacional.
O ImobIA não substitui orientação profissional.


## Fase 6 — validação real na OCI

A Fase 6 adiciona scripts operacionais para preparar e validar o ambiente real.

Sequência:

```bash
python scripts/check_environment.py
python scripts/check_oci_auth.py
python scripts/check_genai_access.py
python scripts/build_index.py
python scripts/phase6_smoke_test.py
streamlit run app/main.py
```

Guia detalhado: [`docs/FASE6_GUIA_EXECUCAO.md`](docs/FASE6_GUIA_EXECUCAO.md)

### Segurança

O arquivo `.env`, `~/.oci/config` e as chaves privadas OCI nunca devem ser
versionados no GitHub.


## Fase 7 — Interface conversacional

A interface Streamlit foi refinada para apresentação:

- histórico de conversa;
- perguntas sugeridas;
- respostas em formato de chat;
- fontes por resposta;
- indicadores da base;
- nova conversa;
- feedback visual de pergunta fora da base;
- cache dos recursos de produção.

Execute:

```bash
streamlit run app/main.py
```


## Fase 8 — Avaliação formal

Execute:

```bash
python -m scripts.run_evaluation
```

A bateria contém 22 casos e gera relatórios em `evaluation/results/`.


### Calibração Fase 8.1

Após a primeira bateria formal, o limiar de relevância foi calibrado para
`0.32` e a avaliação passou a distinguir respostas de guardrail fundamentadas
de recusas por ausência de contexto.


## GitHub

O projeto foi preparado para publicação no repositório público
`ocesarmarques/Challenge-Alura-Agente`.

A publicação executa uma auditoria automática para impedir o versionamento de
`.env`, chaves PEM/KEY e outros artefatos locais.
