# Task Management API — DevSecOps Capstone Starter

A simple Flask + PostgreSQL backend for a Month 6 DevSecOps capstone. The **application is supplied**; the student builds the CI/CD, Kubernetes, security and monitoring systems.

## Requirements
- Docker Engine with Docker Compose plugin (recommended)
- Or Python 3.12+ for standalone testing

## Run with Docker

```bash
cp .env.example .env
# EDIT .env AND REPLACE THE SAMPLE PASSWORD BEFORE RUNNING
docker compose up -d --build
docker compose ps
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

The API is bound to localhost only. PostgreSQL is not exposed outside the Compose network.

## Try the API

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Build Jenkins pipeline","description":"Add CI stages"}'
curl http://localhost:8000/api/tasks
curl -X PATCH http://localhost:8000/api/tasks/1 \
  -H 'Content-Type: application/json' -d '{"status":"in_progress"}'
curl http://localhost:8000/api/tasks/1
curl -X DELETE http://localhost:8000/api/tasks/1
```

## API routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | App info |
| GET | `/health` | Process liveness |
| GET | `/ready` | Database readiness |
| GET | `/api` | List endpoints |
| GET | `/api/tasks` | List tasks; optional `?status=todo` |
| GET | `/api/tasks/<id>` | Get task |
| POST | `/api/tasks` | Create task |
| PATCH | `/api/tasks/<id>` | Update task |
| DELETE | `/api/tasks/<id>` | Delete task |

Task statuses: `todo`, `in_progress`, `done`.

## Run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

Tests use isolated SQLite databases, so PostgreSQL isn't required for unit testing.

# task-mgt-capstone
