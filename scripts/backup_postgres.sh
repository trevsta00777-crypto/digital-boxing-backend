#!/usr/bin/env bash
# Logical backup of Postgres for the boxing API.
# Usage:
#   ./scripts/backup_postgres.sh
# Env (or .env): POSTGRES_HOST POSTGRES_PORT POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=boxing}"
: "${POSTGRES_DB:=boxing}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}"

BACKUP_DIR="${BACKUP_DIR:-$ROOT/backups}"
mkdir -p "$BACKUP_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$BACKUP_DIR/${POSTGRES_DB}_${STAMP}.sql.gz"

export PGPASSWORD="$POSTGRES_PASSWORD"
echo "Backing up ${POSTGRES_USER}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB} -> $OUT"
pg_dump \
  --host="$POSTGRES_HOST" \
  --port="$POSTGRES_PORT" \
  --username="$POSTGRES_USER" \
  --dbname="$POSTGRES_DB" \
  --format=plain \
  --no-owner \
  --no-acl \
  | gzip -c > "$OUT"

# Keep last 14 dumps by default
KEEP="${BACKUP_KEEP:=14}"
ls -1t "$BACKUP_DIR"/${POSTGRES_DB}_*.sql.gz 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f

echo "OK: $OUT"
sha256sum "$OUT" > "${OUT}.sha256"
