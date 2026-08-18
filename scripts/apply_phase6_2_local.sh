#!/usr/bin/env bash
set -euo pipefail

echo "=== ImobIA | Aplicando calibração da Fase 6.2 ==="

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "[OK] .env criado a partir do exemplo."
fi

if grep -q '^MIN_RELEVANCE_SCORE=' .env; then
  sed -i 's/^MIN_RELEVANCE_SCORE=.*/MIN_RELEVANCE_SCORE=0.30/' .env
else
  printf '\nMIN_RELEVANCE_SCORE=0.30\n' >> .env
fi

echo "[OK] MIN_RELEVANCE_SCORE=0.30"
echo "Concluído."
