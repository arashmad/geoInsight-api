# GeoInsight API

## Overview

GeoInsight API is a backend-only FastAPI service for geospatial analysis workflows.

It currently supports project and AOI management, PostGIS-backed vector layer metadata, controlled land-use seed data, and AOI-based land-use composition analysis.

## Current Scope

This service currently supports:

- Health checks (`/health`, `/health/db`)
- Project CRUD
- AOI CRUD
- PostGIS-backed AOI geometry storage
- Vector layer metadata CRUD
- Controlled demo land-use seed data
- Land-use composition analysis by AOI using PostGIS

The API is intentionally backend-only while the core geospatial workflow is being validated.

## Tech Stack

- Python + FastAPI
- PostgreSQL/PostGIS
- SQLAlchemy
- GeoAlchemy2
- Alembic for migrations
- Docker Compose for local orchestration
- Shapely + PyProj for geometry handling
- Pytest for tests
- Ruff for formatting/linting

## Local Development

### Setup

1. Copy the local environment file:

```bash
cp .env.example .env
```

2. Install dependencies using `uv`:

```bash
uv sync --dev
```

### Run with Docker Compose

Start the app and PostGIS:

```bash
docker compose up --build
```

Stop services:

```bash
docker compose down
```

Stop services and remove the local database volume:

```bash
docker compose down -v
```

### Connect to the database

If your shell has the `.env` variables loaded:

```bash
docker exec -it geoinsight-db psql -U "$DATABASE_USER" -d "$DATABASE_NAME"
```

Otherwise, use the values from `.env` directly:

```bash
docker exec -it geoinsight-db psql -U <database_user> -d <database_name>
```

Useful psql commands:

```sql
\dt public.*
\d <table_name>
SELECT * FROM alembic_version;
```

## Database Migrations

Check the current migration revision:

```bash
uv run alembic current
```

Apply the latest migrations:

```bash
uv run alembic upgrade head
```

Create a new migration when needed:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

Check whether models and migrations are in sync:

```bash
uv run alembic check
```

If the local development database has a broken or stale migration state and local data is disposable, reset it:

```bash
docker compose down -v
docker compose up -d db
uv run alembic upgrade head
```

## Seed Data

Seed controlled demo land-use data:

```bash
uv run python scripts/seed_land_use.py
```

This creates one `land_use` vector layer with demo polygon features for:

- forest
- agriculture
- urban
- water
- grassland

## Demo Flow

Assuming the app is running on `http://127.0.0.1:8000`.

### 1) Health checks

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/health/db
```

### 2) Create a project

```bash
curl -s -X POST http://127.0.0.1:8000/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo project",
    "description": "Project for local API walkthrough"
  }'
```

### 3) List projects

```bash
curl -s http://127.0.0.1:8000/v1/projects
```

### 4) Create an AOI under a project

Replace `<project_id>` with an ID returned by the create/list project calls.

```bash
curl -s -X POST http://127.0.0.1:8000/v1/projects/<project_id>/aois \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo AOI",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [44.50, 40.10],
        [44.51, 40.10],
        [44.51, 40.11],
        [44.50, 40.11],
        [44.50, 40.10]
      ]]
    }
  }'
```

### 5) List AOIs for a project

```bash
curl -s http://127.0.0.1:8000/v1/projects/<project_id>/aois
```

### 6) Seed demo land-use data

```bash
uv run python scripts/seed_land_use.py
```

### 7) List vector layers

```bash
curl -s http://127.0.0.1:8000/v1/vector-layers
```

Copy the ID of the seeded `land_use` vector layer.

### 8) Run land-use composition analysis

Replace `<aoi_id>` and `<layer_id>` with real IDs.

```bash
curl -s -X POST http://127.0.0.1:8000/v1/aois/<aoi_id>/land-use-composition \
  -H "Content-Type: application/json" \
  -d '{
    "layer_id": "<layer_id>"
  }'
```

## API Endpoints

### Health

- `GET /health`
- `GET /health/db`

### Projects

- `POST /v1/projects`
- `GET /v1/projects`
- `GET /v1/projects/{project_id}`
- `PATCH /v1/projects/{project_id}`
- `DELETE /v1/projects/{project_id}`

### AOIs

- `POST /v1/projects/{project_id}/aois`
- `GET /v1/projects/{project_id}/aois`
- `GET /v1/aois/{aoi_id}`
- `PATCH /v1/aois/{aoi_id}`
- `DELETE /v1/aois/{aoi_id}`

### Vector Layers

- `POST /v1/vector-layers`
- `GET /v1/vector-layers`
- `GET /v1/vector-layers/{layer_id}`
- `DELETE /v1/vector-layers/{layer_id}`

### Vector Analysis

- `POST /v1/aois/{aoi_id}/land-use-composition`

## Formatting

Run formatting locally:

```bash
uv run ruff format .
uv run ruff check . --fix
```

## Tests

Run all tests locally:

```bash
uv run pytest
```

Run a focused test file:

```bash
uv run pytest tests/<test_file_name>.py
```

The database tests require the PostGIS container to be running and migrations to be applied.

## Next Milestone

The next milestone is focused on exposing persisted vector analysis results, including:

- result detail endpoint
- AOI-level result listing endpoint
- stronger spatial correctness tests

## CI

Pull requests and pushes to `main` are checked by GitHub Actions.

The CI workflow runs:

- Alembic migrations
- Alembic migration consistency check
- Ruff formatting check
- Ruff lint check
- Pytest

CI uses a disposable PostGIS service container and does not require external database secrets.
