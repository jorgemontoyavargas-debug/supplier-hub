#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_ROOT"
OUTPUT_DIRECTORY=${1:-./backups}
TIMESTAMP=$(date -u +%Y%m%d-%H%M%S)
TARGET="$OUTPUT_DIRECTORY/$TIMESTAMP"
mkdir -p "$TARGET"

docker compose exec -T db pg_dump -U supplier_hub -d supplier_hub -Fc > "$TARGET/database.dump"
docker compose exec -T web tar -czf - -C /app media > "$TARGET/media.tar.gz"

if command -v sha256sum >/dev/null 2>&1; then
  (cd "$TARGET" && sha256sum database.dump media.tar.gz > SHA256SUMS.txt)
else
  (cd "$TARGET" && shasum -a 256 database.dump media.tar.gz > SHA256SUMS.txt)
fi

printf '%s\n' "$TARGET"

