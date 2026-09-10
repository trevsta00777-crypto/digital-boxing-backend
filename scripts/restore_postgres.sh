#!/usr/bin/env bash
# Restore a gzipped plain SQL dump created by backup_postgres.sh
# Usage:
#   ./scripts/restore_postgres.sh backups/boxing_20260101T000000Z.sql.gz
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <backup.sql.gz>" >&2
  exit 1
fi
DUMP="$1"
if [[ ! -f "$DUMP" ]]; then
  echo "File not found: $DUMP" >&2
  exit 1
fi

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

export PGPASSWORD="$POSTGRES_PASSWORD"
echo "WARNING: This will apply $DUMP onto ${POSTGRES_DB}@${POSTGRES_HOST}"
read -r -p "Type YES to continue: " CONFIRM
[[ "$CONFIRM" == "YES" ]] || { echo "Aborted"; exit 1; }

gunzip -c "$DUMP" | psql \
  --host="$POSTGRES_HOST" \
  --port="$POSTGRES_PORT" \
  --username="$POSTGRES_USER" \
  --dbname="$POSTGRES_DB" \
  --single-transaction \
  --set ON_ERROR_STOP=on

echo "Restore complete."
