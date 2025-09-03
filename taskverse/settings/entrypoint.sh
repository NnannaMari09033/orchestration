#!/bin/bash

set -euo pipefail

# Wait for database
if [ -n "${DB_HOST:-}" ]; then
  echo "Waiting for Postgres at ${DB_HOST}:${DB_PORT:-5432}..."
  until nc -z ${DB_HOST} ${DB_PORT:-5432}; do
    sleep 0.5
  done
  echo "Postgres is up"
fi

# Wait for Redis
if [ -n "${REDIS_HOST:-}" ]; then
  echo "Waiting for Redis at ${REDIS_HOST}:6379..."
  until nc -z ${REDIS_HOST} 6379; do
    sleep 0.5
  done
  echo "Redis is up"
fi


if [ "${SKIP_DJANGO_BOOTSTRAP:-0}" != "1" ]; then
  # Run migrations
  python manage.py migrate --noinput

  # Create superuser if specified
  if [ "${CREATE_SUPERUSER:-0}" = "1" ]; then
    echo "Creating superuser..."
    python manage.py shell << PYEOF
from django.contrib.auth import get_user_model
User = get_user_model()
email = '${DJANGO_SUPERUSER_EMAIL:-admin@taskverse.com}'
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        full_name='${DJANGO_SUPERUSER_FULL_NAME:-Admin}',
        password='${DJANGO_SUPERUSER_PASSWORD:-adminpassword}'
    )
    print('Superuser created')
else:
    print('Superuser already exists')
PYEOF
  fi

  # Collect static files
  python manage.py collectstatic --noinput || true
fi


# Execute the main command
exec "$@"
