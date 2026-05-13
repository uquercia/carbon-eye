#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NO_CACHE="${1:-}"

cd "$SCRIPT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "未检测到 docker，请先执行 install-docker-alinux3.sh。"
  exit 1
fi

if [ ! -f ".env" ]; then
  cp .env.server.example .env
  echo "已生成 .env，请先按服务器实际配置修改后再重新执行。"
  exit 1
fi

mkdir -p "$SCRIPT_DIR/mysql/init"

# 首次部署优先导入完整数据；如果没有数据转储，则至少导入建库建表 SQL。
if [ ! -f "$SCRIPT_DIR/mysql/init/001-carbon_eye_dump.sql" ] && [ ! -f "$SCRIPT_DIR/mysql/init/001-database-schema.sql" ]; then
  if [ -f "$PROJECT_ROOT/deploy_artifacts/carbon_eye_dump.sql" ]; then
    cp "$PROJECT_ROOT/deploy_artifacts/carbon_eye_dump.sql" "$SCRIPT_DIR/mysql/init/001-carbon_eye_dump.sql"
  elif [ -f "$PROJECT_ROOT/docs/database-schema.sql" ]; then
    cp "$PROJECT_ROOT/docs/database-schema.sql" "$SCRIPT_DIR/mysql/init/001-database-schema.sql"
  fi
fi

if [ "$NO_CACHE" = "--no-cache" ]; then
  echo "检测到 --no-cache，开始无缓存重建 api 和 web。"
  docker compose -f docker-compose.server-build.yml build --no-cache api web
else
  docker compose -f docker-compose.server-build.yml build api web
fi

docker compose -f docker-compose.server-build.yml up -d --force-recreate api web
docker compose -f docker-compose.server-build.yml ps
