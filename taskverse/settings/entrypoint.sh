#!/bin/bash

set -euo pipefail

# Wait for database
echo "Waiting for Postgres at ${DB_HOST:-postgres}:${DB_PORT:-5432}..."
until nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do
  sleep 0.5
done
echo "Postgres is up"

# Wait for Redis
echo "Waiting for Redis at ${REDIS_HOST:-redis}:6379..."
until nc -z ${REDIS_HOST:-redis} 6379; do
  sleep 0.5
done
echo "Redis is up"

if [ "${SKIP_DJANGO_BOOTSTRAP:-0}" != "1" ]; then
  # Run migrations
  echo "Running migrations..."
  python manage.py makemigrations --noinput
  python manage.py migrate

  # Create superuser if it doesn't exist
  echo "Creating superuser..."
  python manage.py shell << PYEOF
from django.contrib.auth import get_user_model
User = get_user_model()
email = 'admin@taskverse.com'
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, full_name='Admin', password='adminpassword')
    print('Superuser created')
else:
    print('Superuser already exists')
PYEOF

  # Collect static files
  python manage.py collectstatic --noinput || true
fi

# Execute the main command
exec "$@"
