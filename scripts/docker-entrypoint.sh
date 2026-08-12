#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "${SUPPLIER_HUB_SEED_DEMO:-false}" = "true" ]; then
  python manage.py seed_demo
fi

exec "$@"
