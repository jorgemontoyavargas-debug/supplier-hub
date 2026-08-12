#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_ROOT"
PYTHON_EXECUTABLE=.venv/bin/python

"$PYTHON_EXECUTABLE" manage.py check
"$PYTHON_EXECUTABLE" manage.py makemigrations --check --dry-run
"$PYTHON_EXECUTABLE" manage.py test
"$PYTHON_EXECUTABLE" manage.py evaluate_local_ai
"$PYTHON_EXECUTABLE" manage.py collectstatic --noinput --verbosity 0

SUPPLIER_HUB_DEBUG=false \
SUPPLIER_HUB_HTTPS=true \
SUPPLIER_HUB_SECRET_KEY=verify-only-secret-key-with-more-than-fifty-characters-1234567890 \
SUPPLIER_HUB_ALLOWED_HOSTS=localhost,127.0.0.1,testserver \
SUPPLIER_HUB_HSTS_PRELOAD=true \
"$PYTHON_EXECUTABLE" manage.py check --deploy --fail-level WARNING

echo "Verificación completada."

