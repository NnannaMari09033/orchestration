# Taskverse Orchestration

A containerized Django application for orchestrating background tasks with Celery, Redis, and PostgreSQL. It exposes a GraphQL API (Graphene) and includes operational tooling via Flower. The stack is built and run with Docker Compose for local development and can be adapted for production deployments.

## Contents
- Overview
- Architecture
- Tech stack
- Local development (Docker Compose)
- Configuration (environment variables)
- Database & migrations
- GraphQL API quickstart
- Celery (worker, beat) and Flower
- Static files
- Project layout
- Production notes
- Troubleshooting
- Contributing

## Overview
This service manages user-submitted tasks and monitoring records. It uses:
- Django as the web framework
- Graphene-Django for a GraphQL API at `/graphql`
- Celery for asynchronous task execution (worker) and periodic scheduling (beat)
- Redis as Celery broker/result backend
- PostgreSQL as the relational database
- Flower to monitor Celery at `/` on port `5555`

## Architecture
Services (docker-compose):
- `web`: Django app + GraphQL; runs via `manage.py runserver` in dev.
- `worker`: Celery worker (`celery -A taskverse worker`).
- `beat`: Celery beat scheduler (`celery -A taskverse beat`).
- `flower`: Celery monitoring UI (`celery -A taskverse flower`).
- `redis`: Broker/result backend.
- `postgres`: Primary database.

Django apps:
- `taskverse.apps.users` (custom user model, email as username)
- `taskverse.apps.tasks` (task model & GraphQL schema)
- `taskverse.apps.monitoring` (monitoring model & GraphQL schema)
- `taskverse.apps.notifications` (notification model)

GraphQL schema:
- Combined in `taskverse/schema.py` and wired via `GRAPHENE['SCHEMA']`.
- GraphiQL UI is enabled at `/graphql` for local development.

Celery configuration:
- App defined in `taskverse/settings/celery.py`.
- Broker/result default to `redis://redis:6379/0` in containers.
- Auto-discovers tasks from installed apps.

## Tech stack
- Python 3.11 (slim)
- Django 5.2.x
- Celery 5.5.x
- Redis 7 (alpine)
- PostgreSQL 15
- Graphene-Django 3.2.x
- Django REST Framework 3.16.x (available; not primary API)
- django-environ for env configuration
- django-celery-beat & django-celery-results for scheduling/results
- Flower 2.x
- Docker & Docker Compose

## Local development (Docker Compose)
Prerequisites: Docker and Docker Compose.


Start the full stack:
```bash
docker compose up -d --build
```

Check service status:
```bash
docker compose ps
```

Tail logs for a service (examples):
```bash
# Web (Django)
docker compose logs --no-color -f web
# Celery worker
docker compose logs --no-color -f worker
# Celery beat
docker compose logs --no-color -f beat
# Flower
docker compose logs --no-color -f flower
```

Endpoints:
- Web (Django): http://localhost:8000/
- Admin: http://localhost:8000/admin
- GraphQL: http://localhost:8000/graphql
- Flower: http://localhost:5555/

Default superuser (created automatically by entrypoint):
- Email: `admin@taskverse.com`
- Password: `adminpassword`

Note: The entrypoint script waits for Postgres and Redis, runs migrations, creates the superuser (if missing), and collects static files on the `web` service only.

## Configuration (environment variables)
Django reads configuration with `django-environ` and from container env vars. Common variables:
- `DJANGO_SETTINGS_MODULE`: defaults to `taskverse.django.local` in dev
- `SECRET_KEY`: Django secret key
- Database:
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`
  - `DB_HOST` (in Compose: `postgres`)
  - `DB_PORT` (default `5432`)
- Celery:
  - `CELERY_BROKER_URL` (default `redis://redis:6379/0` in containers)
  - `CELERY_RESULT_BACKEND` (default `redis://redis:6379/0`)
- Optional:
  - `DJANGO_DEBUG` (default `True` in local)
  - `ALLOWED_HOSTS` (comma-separated for production)
  - `SKIP_DJANGO_BOOTSTRAP` (set to `1` on worker/beat/flower to skip migrations/superuser/static)

You can also place a `.env` file at project root; it will be read by `taskverse/env.py`.

Example `.env` (do not commit secrets):
```env
SECRET_KEY=replace-me
DJANGO_DEBUG=True
DB_NAME=taskverse_db
DB_USER=taskverse_user
DB_PASSWORD=strong-password
DB_HOST=localhost
DB_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Database & migrations
Apply migrations (web container runs these automatically on start):
```bash
docker compose exec web python manage.py migrate
```

Create a superuser (if you want custom credentials):
```bash
docker compose exec web python manage.py createsuperuser
```

Auto-creation (web entrypoint):
- Runs `makemigrations` and `migrate`
- Creates `admin@taskverse.com` if missing
- Runs `collectstatic` into `STATIC_ROOT`

## GraphQL API quickstart
GraphiQL explorer at `/graphql` (development only).

Available operations (from codebase):
- Query:
  - `all_tasks: [TaskType]`
  - `task_by_id(id: Int!): TaskType`
  - `all_monitoring_records: [MonitoringRecordType]`
  - `monitoring_record_by_id(id: Int!): MonitoringRecordType`
  - `me: UserType` (returns current authenticated user, otherwise `null`)
- Mutation:
  - `create_task(name: String!): TaskType` (requires authenticated user)

Examples:
```graphql
# List tasks
query {
  all_tasks { id name status createdAt }
}
```

```graphql
# Get a task by ID
query($id: Int!) {
  task_by_id(id: $id) { id name status }
}
```

```graphql
# Create a task (must be authenticated)
mutation {
  create_task(name: "Example Task") {
    task { id name status }
  }
}
```

Authentication notes:
- The `me` query and `create_task` mutation depend on an authenticated session (`request.user`).
- In local dev, you can log into the Django admin in the same browser, then use GraphiQL to carry the session cookie.
- JWT/OAuth is not wired; DRF is present but not used for primary endpoints.

## Celery and Flower
Start/stop from Docker Compose (already handled by `up -d`):
- Worker: `celery -A taskverse worker --loglevel=info`
- Beat: `celery -A taskverse beat --loglevel=info`
- Flower: `celery -A taskverse flower` (UI on port 5555)

Scheduler/results apps are installed:
- `django_celery_beat` (periodic tasks)
- `django_celery_results` (task results)

Configure periodic tasks via Django Admin (Periodic tasks section) once migrations are applied.

## Static files
- `STATIC_URL = /static/`
- `STATIC_ROOT = <project>/staticfiles`
- `collectstatic` is executed by the web entrypoint on startup in dev.

## Project layout
```
.
├─ docker-compose.yml
├─ Dockerfile
├─ manage.py
├─ requirements.txt
└─ taskverse/
   ├─ __init__.py
   ├─ asgi.py
   ├─ wsgi.py
   ├─ urls.py
   ├─ schema.py                 # GraphQL root schema
   ├─ env.py                    # django-environ setup
   ├─ django/
   │  ├─ base.py               # base settings
   │  ├─ local.py              # local settings
   │  ├─ production.py         # production settings
   ├─ settings/
   │  ├─ celery.py             # Celery app config
   │  └─ entrypoint.sh         # container entrypoint
   └─ apps/
      ├─ users/
      ├─ tasks/
      ├─ monitoring/
      └─ notifications/
```

## Production Deployment
This project includes a production-ready setup using Docker Compose.

### Prerequisites
- Docker and Docker Compose
- A `.env.prod` file with your production configuration. You can use `.env.prod.example` as a template.

### Configuration
Create a `.env.prod` file in the root of the project and add your production-specific environment variables. At a minimum, you should set:
- `SECRET_KEY`: A long, random string.
- `ALLOWED_HOSTS`: A comma-separated list of your domain names (e.g., `example.com,www.example.com`).
- `DATABASE_URL`: The URL of your production PostgreSQL database.
- `CELERY_BROKER_URL`: The URL of your production Redis instance.
- `CELERY_RESULT_BACKEND`: The URL of your production Redis instance.
- `FLOWER_USER`: The username for the Flower dashboard.
- `FLOWER_PASSWORD`: The password for the Flower dashboard.

### Running in Production
To build and run the application in production mode, use the `docker-compose.prod.yml` file:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Running Migrations
To run database migrations in your production environment, you can use the `web` service:
```bash
docker-compose -f docker-compose.prod.yml run --rm web /entrypoint.sh /bin/bash -c "python manage.py migrate"
```
Alternatively, you can set the `RUN_MIGRATIONS` environment variable to `1` in your `.env.prod` file to run migrations automatically when the `web` service starts.

### Creating a Superuser
To create a superuser in your production environment, you can use the `web` service:
```bash
docker-compose -f docker-compose.prod.yml run --rm web /entrypoint.sh /bin/bash -c "python manage.py createsuperuser"
```
Alternatively, you can set the `CREATE_SUPERUSER` environment variable to `1` in your `.env.prod` file to create a superuser automatically when the `web` service starts. You can also set the `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_FULL_NAME`, and `DJANGO_SUPERUSER_PASSWORD` environment variables to customize the superuser.

## Deploying to Render

This project is configured for deployment on [Render](https://render.com/) using a `render.yaml` file. Render will automatically build and deploy the services defined in this file when you push changes to your Git repository.

### Setup

1.  **Push to Git:** Make sure all your latest changes, including the `render.yaml` file, are committed and pushed to your GitHub, GitLab, or Bitbucket repository.

2.  **Create a Blueprint on Render:**
    *   Navigate to the [Render Dashboard](https://dashboard.render.com/) and click "New" -> "Blueprint".
    *   Connect your Git repository.
    *   Render will detect the `render.yaml` file and show you the services that will be created.

3.  **Set Environment Variables:**
    *   Render will automatically provision a PostgreSQL database and a Redis instance and inject their connection URLs into your services.
    *   You will need to add secrets like `SECRET_KEY`, `FLOWER_USER`, and `FLOWER_PASSWORD` to your environment. The recommended way to do this is by creating an **Environment Group** in Render and adding your secrets there. You can then link this group to all your services (`taskverse-web`, `taskverse-worker`, `taskverse-beat`, and `taskverse-flower`).

4.  **Deploy:**
    *   Click "Create" to deploy your services. Render will build the Docker image, run migrations (as defined by the `preDeployCommand`), and start your web, worker, beat, and flower services.

Your application will be live at the URL provided by Render for the `taskverse-web` service. The Flower dashboard will be available at the URL for the `taskverse-flower` service.

## Production notes
- Use `taskverse.django.production` and set `DJANGO_SETTINGS_MODULE` accordingly.
- Replace `runserver` with Gunicorn/Uvicorn for WSGI/ASGI.
- Serve static files via a web server (e.g., Nginx) and remove `collectstatic` from runtime if prebuilt.
- Use managed services for Postgres/Redis and secrets from a secure store.
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`.
- Run database migrations as part of deployment (one-off task).

## Troubleshooting
- Staticfiles ImproperlyConfigured: Ensure `STATIC_ROOT` is set (already configured) and that `collectstatic` completes.
- Database connection errors: Check `DB_*` env vars; Postgres may still be starting—Compose healthcheck waits for readiness.
- Celery cannot connect to broker: Confirm `CELERY_BROKER_URL` and that `redis` service is healthy.
- GraphQL mutations failing with auth errors: Ensure you’re authenticated (log into `/admin` first) or add an auth layer (JWT) if needed.
- Duplicate migrations table errors in non-web services: Avoid running migrations in worker/beat/flower; this repo sets `SKIP_DJANGO_BOOTSTRAP=1` for them.

## Contributing
- Open an issue to discuss significant changes.
- Keep PRs focused and include tests when adding behavior.
- Follow Django, Celery, and Graphene best practices.

---

Maintainers can extend this README with SLOs, SLIs, runbooks, and deployment diagrams as the system evolves.
