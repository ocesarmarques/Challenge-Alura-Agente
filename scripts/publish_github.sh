#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${HOME}/Downloads/Challenge-Alura-Agente"
REPO_URL="https://github.com/ocesarmarques/Challenge-Alura-Agente.git"

echo "=== ImobIA | Publicação GitHub ==="
echo "Origem: ${SOURCE_DIR}"
echo "Destino: ${TARGET_DIR}"
echo

cd "${SOURCE_DIR}"
python -m scripts.security_audit

if ! command -v git >/dev/null 2>&1; then
  echo "[ERRO] Git não está instalado."
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "[ERRO] rsync não está instalado."
  exit 1
fi

if [ -d "${TARGET_DIR}/.git" ]; then
  echo "[INFO] Repositório local já existe. Atualizando..."
  git -C "${TARGET_DIR}" pull --ff-only origin main
else
  if [ -e "${TARGET_DIR}" ]; then
    echo "[ERRO] ${TARGET_DIR} já existe e não é um clone Git."
    echo "Renomeie ou remova essa pasta antes de continuar."
    exit 1
  fi

  git clone "${REPO_URL}" "${TARGET_DIR}"
fi

echo "[INFO] Copiando projeto sem credenciais e artefatos locais..."

rsync -a --delete \
  --exclude='.git/' \
  --exclude='.venv/' \
  --exclude='venv/' \
  --exclude='.env' \
  --exclude='*.pem' \
  --exclude='*.key' \
  --exclude='__pycache__/' \
  --exclude='.pytest_cache/' \
  --exclude='data/vector_store/*' \
  --exclude='evaluation/results/*' \
  "${SOURCE_DIR}/" "${TARGET_DIR}/"

mkdir -p "${TARGET_DIR}/data/vector_store"
touch "${TARGET_DIR}/data/vector_store/.gitkeep"
mkdir -p "${TARGET_DIR}/evaluation/results"
touch "${TARGET_DIR}/evaluation/results/.gitkeep"

cd "${TARGET_DIR}"

if ! git config user.name >/dev/null; then
  git config user.name "César Marques"
fi

if ! git config user.email >/dev/null; then
  git config user.email "cesarr.marques@gmail.com"
fi

# Registra remoções de arquivos que já eram rastreados.
git add -u

commit_if_needed() {
  local message="$1"
  shift

  local existing=()
  local path

  for path in "$@"; do
    if [ -e "${path}" ]; then
      existing+=("${path}")
    else
      echo "[INFO] Caminho opcional ausente, ignorando: ${path}"
    fi
  done

  if [ ${#existing[@]} -gt 0 ]; then
    git add -- "${existing[@]}"
  fi

  if ! git diff --cached --quiet; then
    git commit -m "${message}"
  else
    echo "[INFO] Sem alterações para commit: ${message}"
  fi
}

commit_if_needed \
  "chore: prepare project structure and secure configuration" \
  .gitignore .dockerignore .env.example requirements.txt Dockerfile \
  app/__init__.py app/config.py \
  data/vector_store/.gitkeep evaluation/results/.gitkeep

commit_if_needed \
  "feat: add real estate knowledge base and document processing" \
  data/documents \
  app/rag/__init__.py app/rag/loader.py app/rag/chunker.py app/rag/pipeline.py \
  docs/arquitetura.md

commit_if_needed \
  "feat: implement OCI embeddings, FAISS retrieval and grounded agent" \
  app/rag/embeddings.py app/rag/vector_store.py app/rag/retriever.py \
  app/agent app/services \
  scripts/build_index.py scripts/ask.py scripts/search_demo.py \
  docs/fase4.md docs/fase5.md

commit_if_needed \
  "feat: add conversational Streamlit interface" \
  app/main.py app/ui \
  docs/FASE7_UX_INTERFACE.md

commit_if_needed \
  "test: add automated tests and RAG evaluation suite" \
  tests \
  evaluation/test_cases.json evaluation/review_template.md \
  app/evaluation \
  scripts/run_evaluation.py scripts/calibrate_retrieval.py \
  scripts/phase6_smoke_test.py \
  docs/FASE8_TESTES_METRICAS.md docs/FASE8_1_CALIBRACAO.md \
  docs/testes.md

commit_if_needed \
  "docs: add OCI setup, validation and project utilities" \
  scripts/setup_local.sh scripts/setup_local.ps1 scripts/run_tests.sh \
  scripts/check_environment.py scripts/check_oci_auth.py \
  scripts/check_genai_access.py scripts/apply_phase6_2_local.sh \
  scripts/apply_phase8_1_local.py scripts/security_audit.py \
  scripts/publish_github.sh \
  docs/CALIBRACAO_FASE6_2.md docs/CORRECAO_EMBEDDINGS_FASE6_1.md \
  docs/FASE6_GUIA_EXECUCAO.md docs/POLITICAS_OCI.md \
  docs/VALIDACAO_FASE4.md docs/VALIDACAO_FASE5.md \
  docs/VALIDACAO_FASE6.md docs/VALIDACAO_FASE7.md \
  docs/VALIDACAO_FASE8.md docs/VALIDACAO_FASE8_1.md \
  docs/VALIDACAO_FASE9.md docs/FASE9_GITHUB.md

commit_if_needed \
  "docs: update project README through evaluation phase" \
  README.md

echo
echo "[INFO] Auditoria final do repositório..."
python -m scripts.security_audit

echo
echo "=== Histórico preparado ==="
git --no-pager log --oneline --decorate -12
echo

echo "[INFO] Enviando branch main para GitHub..."
git push -u origin main

echo
echo "[OK] Publicação concluída."
echo "Repositório: https://github.com/ocesarmarques/Challenge-Alura-Agente"
