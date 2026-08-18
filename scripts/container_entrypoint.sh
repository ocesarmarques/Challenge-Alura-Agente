#!/bin/sh
set -eu

echo "=== ImobIA | Inicialização do container ==="
echo "Auth OCI: ${OCI_AUTH_MODE:-config_file}"
echo "Região: ${OCI_REGION:-sa-saopaulo-1}"

INDEX_FILE="data/vector_store/index.faiss"
METADATA_FILE="data/vector_store/metadata.json"

if [ ! -f "$INDEX_FILE" ] || [ ! -f "$METADATA_FILE" ]; then
    echo "[INFO] Índice FAISS ausente. Criando com OCI Generative AI..."
    python -m scripts.build_index
else
    echo "[OK] Índice FAISS existente."
fi

echo "[INFO] Iniciando Streamlit na porta 8501..."
exec python -m streamlit run app/main.py \
    --server.address=0.0.0.0 \
    --server.port=8501 \
    --server.headless=true
