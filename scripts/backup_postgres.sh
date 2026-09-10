#!/usr/bin/env bash
# Logical backup of Postgres for the boxing API.
# Default target: host volume mount at /backups (see docker-compose*.yml:
#   ./backups:/backups on the db service). On the host, dumps appear in ./backups/.
#
# Usage:
#   ./scripts/backup_postgres.sh
#   BACKUP_DIR=/backups ./scripts/backup_postgres.sh
#   ./scripts/backup_via_compose.sh          # recommended in Docker Compose
#
# Env (or .env): POSTGRES_HOST POSTGRES_PORT POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB
# Optional: BACKUP_DIR (default /backups if writable, else ./backups), BACKUP_KEEP (default 14)
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

# Prefer the Compose host-volume mount point (/backups → ./backups on the host).
if [[ -n "${BACKUP_DIR:-}" ]]; then
  :
elif [[ -d /backups ]] && [[ -w /backups ]]; then
  BACKUP_DIR=/backups
else
  BACKUP_DIR="$ROOT/backups"
fi

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

KEEP="${BACKUP_KEEP:=14}"
ls -1t "$BACKUP_DIR"/${POSTGRES_DB}_*.sql.gz 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f
# prune matching checksums for removed dumps
ls -1t "$BACKUP_DIR"/${POSTGRES_DB}_*.sql.gz.sha256 2>/dev/null | while read -r sum; do
  [[ -f "${sum%.sha256}" ]] || rm -f "$sum"
done

echo "OK: $OUT"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "$OUT" > "${OUT}.sha256"
elif command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "$OUT" > "${OUT}.sha256"
fi
