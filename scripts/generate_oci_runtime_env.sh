#!/bin/sh
set -eu

IMDS="http://169.254.169.254/opc/v2/instance"
AUTH_HEADER="Authorization: Bearer Oracle"

echo "=== ImobIA | Gerando ambiente OCI Compute ==="

COMPARTMENT_ID="$(
  curl -fsS -H "$AUTH_HEADER" \
    "$IMDS/compartmentId"
)"

REGION="$(
  curl -fsS -H "$AUTH_HEADER" \
    "$IMDS/canonicalRegionName"
)"

if [ -z "$COMPARTMENT_ID" ] || [ -z "$REGION" ]; then
    echo "[ERRO] Não foi possível ler o IMDSv2."
    exit 1
fi

cat > .env.production <<EOF
APP_TITLE=ImobIA
TOP_K=5
MIN_RELEVANCE_SCORE=0.32
CHUNK_SIZE=900
CHUNK_OVERLAP=120

OCI_AUTH_MODE=instance_principal
OCI_REGION=${REGION}
OCI_COMPARTMENT_ID=${COMPARTMENT_ID}
OCI_GENAI_ENDPOINT=

OCI_EMBEDDING_MODEL_ID=cohere.embed-v4.0
EMBEDDING_DIMENSIONS=1024
EMBEDDING_BATCH_SIZE=32

OCI_CHAT_MODEL_ID=cohere.command-a-03-2025
CHAT_TEMPERATURE=0.10
CHAT_MAX_TOKENS=700
EOF

chmod 600 .env.production

echo "[OK] .env.production criado."
echo "[OK] Região detectada: ${REGION}"
echo "[OK] Compartment detectado via IMDSv2."
