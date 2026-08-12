#!/bin/sh
set -eu

if [ "${CONFIRM_RESTORE:-}" != "yes" ]; then
  echo "La restauración reemplaza los datos actuales. Define CONFIRM_RESTORE=yes." >&2
  exit 2
fi

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_ROOT"
BACKUP_DIRECTORY=${1:?Indica el directorio de la copia}
BACKUP_DIRECTORY=$(CDPATH= cd -- "$BACKUP_DIRECTORY" && pwd)
ALLOWED_ROOT="$PROJECT_ROOT/backups"
case "$BACKUP_DIRECTORY" in
  "$ALLOWED_ROOT"/*) ;;
  *) echo "La copia debe estar dentro de $ALLOWED_ROOT" >&2; exit 2 ;;
esac

test -f "$BACKUP_DIRECTORY/database.dump"
test -f "$BACKUP_DIRECTORY/media.tar.gz"

docker compose stop web
docker compose exec -T db psql -U supplier_hub -d postgres -v ON_ERROR_STOP=1 \
  -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='supplier_hub' AND pid <> pg_backend_pid();"
docker compose exec -T db dropdb -U supplier_hub --if-exists supplier_hub
docker compose exec -T db createdb -U supplier_hub supplier_hub
docker compose exec -T db pg_restore -U supplier_hub -d supplier_hub < "$BACKUP_DIRECTORY/database.dump"
docker compose start web

attempt=0
until docker compose exec -T web python manage.py check >/dev/null 2>&1; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    echo "La aplicación no regresó después de restaurar." >&2
    exit 1
  fi
  sleep 2
done

docker compose exec -T web sh -c 'find /app/media -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +'
docker compose exec -T web tar -xzf - -C /app < "$BACKUP_DIRECTORY/media.tar.gz"
docker compose exec -T web python manage.py migrate --check

echo "Restauración completada."

