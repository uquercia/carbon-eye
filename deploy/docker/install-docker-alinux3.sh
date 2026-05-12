#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "请使用 root 执行。"
  exit 1
fi

dnf -y update
dnf -y install docker docker-compose-plugin

systemctl enable --now docker

docker --version
docker compose version
