# Fase 6 — Configuração local + OCI + validação ponta a ponta

## Objetivo

A Fase 6 transforma a implementação das fases anteriores em uma execução real
na tenancy OCI do usuário.

## Resultado esperado

Ao final desta fase:

- ambiente Python funcionando;
- cinco PDFs detectados;
- autenticação OCI funcionando;
- permissões de Chat e Embeddings funcionando;
- índice FAISS criado com embeddings reais;
- pergunta dentro da base respondida;
- pergunta fora da base tratada;
- Streamlit executando localmente.

---

## Parte A — Ambiente local

### Windows PowerShell

Na raiz do projeto:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup_local.ps1
```

Depois:

```powershell
python scripts\check_environment.py
```

### Linux/macOS/WSL

```bash
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
python scripts/check_environment.py
```

---

## Parte B — OCI API Signing Key

A autenticação local do projeto usa o arquivo OCI SDK/CLI `~/.oci/config`.

No Console OCI:

1. Abra o menu do perfil.
2. Entre em **User settings**.
3. Entre em **Tokens and keys**.
4. Em **API keys**, adicione uma chave.
5. Salve a chave privada em local seguro.
6. Copie o snippet de configuração fornecido pela OCI para `~/.oci/config`.
7. Garanta que `key_file` aponte para a chave privada correta.

Exemplo estrutural:

```ini
[DEFAULT]
user=ocid1.user...
fingerprint=...
tenancy=ocid1.tenancy...
region=sa-saopaulo-1
key_file=/caminho/seguro/oci_api_key.pem
```

Nunca envie `config`, chave `.pem`, fingerprint ou secrets para o GitHub.

---

## Parte C — Permissões mínimas do Generative AI

Se o usuário já estiver no grupo Administrators, esta etapa pode não exigir uma
nova policy.

Para um grupo comum, o projeto precisa no mínimo das operações de Chat e
EmbedText no compartment escolhido:

```text
Allow group <NOME_DO_GRUPO> to use generative-ai-chat in compartment <NOME_DO_COMPARTMENT>
Allow group <NOME_DO_GRUPO> to use generative-ai-text-embedding in compartment <NOME_DO_COMPARTMENT>
```

Use os nomes reais do grupo e do compartment.

---

## Parte D — Compartment OCID

No Console OCI:

1. Abra **Identity & Security**.
2. Abra **Compartments**.
3. Escolha o compartment do projeto.
4. Copie o **OCID**.
5. Abra o arquivo `.env`.
6. Preencha:

```env
OCI_COMPARTMENT_ID=ocid1.compartment...
```

Não use aspas.

---

## Parte E — Validar autenticação

```bash
python scripts/check_oci_auth.py
```

Resultado desejado:

```text
[OK] OCI respondeu à chamada autenticada
[OK] OCI_COMPARTMENT_ID configurado
RESULTADO: autenticação OCI pronta.
```

---

## Parte F — Validar Generative AI

```bash
python scripts/check_genai_access.py
```

O script faz uma pequena chamada de embedding e uma pequena chamada de chat.

Resultado desejado:

```text
[OK] Embedding retornado com dimensão 1024.
[OK] Chat OCI respondeu.
RESULTADO: acesso ao OCI Generative AI validado.
```

---

## Parte G — Criar índice vetorial real

```bash
python scripts/build_index.py
```

Isso gera:

```text
data/vector_store/index.faiss
data/vector_store/metadata.json
```

Esses arquivos são derivados da base PDF e podem ser regenerados.

---

## Parte H — Teste ponta a ponta

```bash
python scripts/phase6_smoke_test.py
```

O teste executa:

1. uma pergunta dentro da base;
2. uma pergunta deliberadamente fora da base.

Depois execute:

```bash
python scripts/calibrate_retrieval.py
```

Use os scores observados para ajustar `MIN_RELEVANCE_SCORE` se necessário.

---

## Parte I — Interface Streamlit

```bash
streamlit run app/main.py
```

Abra o endereço local informado pelo Streamlit.

Teste pelo menos:

```text
A simulação do financiamento garante aprovação?
```

e:

```text
Qual imóvel de São Paulo terá maior valorização em 2027?
```

---

## Quando considerar a Fase 6 concluída

- `check_environment.py`: sem erros;
- `check_oci_auth.py`: OK;
- `check_genai_access.py`: OK;
- `index.faiss` criado;
- smoke test executado;
- pergunta dentro da base respondida corretamente;
- pergunta fora da base não gera informação inventada;
- Streamlit funcionando localmente.

## Observação sobre modelos e região

Configuração padrão usada:

```env
OCI_REGION=sa-saopaulo-1
OCI_EMBEDDING_MODEL_ID=cohere.embed-v4.0
OCI_CHAT_MODEL_ID=cohere.command-a-03-2025
```

A disponibilidade deve sempre ser confirmada novamente caso a Oracle altere
modelos ou regiões.
