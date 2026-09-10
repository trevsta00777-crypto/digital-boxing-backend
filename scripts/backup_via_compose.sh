#!/usr/bin/env bash
# Run a Postgres dump inside the Compose db container so files land on the
# host volume: ./backups  (mounted as /backups in the container).
#
# Usage (from repo root):
#   ./scripts/backup_via_compose.sh
#   COMPOSE_FILE=docker-compose.prod.yml ./scripts/backup_via_compose.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
if [[ ! -f "$COMPOSE_FILE" ]]; then
  COMPOSE_FILE=docker-compose.yml
fi

mkdir -p "$ROOT/backups"

# Load env for DB name / user (password stays in compose env_file / environment)
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi
: "${POSTGRES_USER:=boxing}"
: "${POSTGRES_DB:=boxing}"
KEEP="${BACKUP_KEEP:=14}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="/backups/${POSTGRES_DB}_${STAMP}.sql.gz"

echo "Using $COMPOSE_FILE — writing host ./backups via container path $OUT"

docker compose -f "$COMPOSE_FILE" exec -T db \
  bash -c "pg_dump -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\" --format=plain --no-owner --no-acl | gzip -c > \"$OUT\" && ls -1t /backups/${POSTGRES_DB}_*.sql.gz 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f && (command -v sha256sum >/dev/null && sha256sum \"$OUT\" > \"${OUT}.sha256\" || true) && echo OK: $OUT"

echo "Host path: $ROOT/backups/${POSTGRES_DB}_${STAMP}.sql.gz"
