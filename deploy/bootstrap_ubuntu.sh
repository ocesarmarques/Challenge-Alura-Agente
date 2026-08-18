#!/bin/bash
set -euo pipefail

REPO_URL="https://github.com/ocesarmarques/Challenge-Alura-Agente.git"
APP_DIR="/opt/imobia"

echo "=== ImobIA | Bootstrap OCI Compute Ubuntu ==="

export DEBIAN_FRONTEND=noninteractive

sudo apt-get update
sudo apt-get install -y ca-certificates curl git

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL \
  https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt-get update
sudo apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

sudo systemctl enable --now docker

if [ -d "${APP_DIR}/.git" ]; then
  sudo git -C "${APP_DIR}" pull --ff-only origin main
else
  sudo rm -rf "${APP_DIR}"
  sudo git clone "${REPO_URL}" "${APP_DIR}"
fi

sudo chown -R "$(id -u):$(id -g)" "${APP_DIR}"

cd "${APP_DIR}"

sh scripts/generate_oci_runtime_env.sh

echo "[INFO] Validando acesso ao IMDS/Instance Principal no host..."
python3 --version

echo "[INFO] Construindo e iniciando o container..."
sudo docker compose \
  -f deploy/docker-compose.oci.yml \
  build --pull

sudo docker compose \
  -f deploy/docker-compose.oci.yml \
  up -d

echo
echo "=== Status ==="
sudo docker compose \
  -f deploy/docker-compose.oci.yml \
  ps

echo
echo "[INFO] Logs:"
sudo docker logs --tail 80 imobia || true

echo
echo "[OK] Bootstrap concluído."
echo "Abra: http://<PUBLIC_IP>:8501"
