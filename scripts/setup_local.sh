#!/usr/bin/env bash
set -euo pipefail

echo "=== ImobIA | Setup local Linux/macOS/WSL ==="

if [ ! -d ".venv" ]; then
  python3.12 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo
  echo "Arquivo .env criado."
  echo "Abra o .env e preencha OCI_COMPARTMENT_ID antes de continuar."
fi

echo
echo "Setup concluído."
echo "Próximo comando: python scripts/check_environment.py"
