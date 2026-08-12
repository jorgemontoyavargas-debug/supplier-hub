#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_ROOT"

PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE:-python3}
if [ ! -x .venv/bin/python ]; then
  "$PYTHON_EXECUTABLE" -m venv .venv
fi

.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py seed_demo

echo "Supplier Hub está preparado."
echo "Ejecuta: .venv/bin/python manage.py runserver"

