# GeoInsight API

## Overview

FastAPI backend for geospatial analysis workflows.

## Current Scope

This service currently supports:

- Health checks (`/health`, `/health/db`)
- Project CRUD basics (create and list projects)
- AOI creation under a project

The API is intentionally minimal while the core geospatial workflow is being validated.

## Tech Stack

- Python + FastAPI
- PostgreSQL/PostGIS
- Alembic for migrations
- Docker Compose for local orchestration

## Local Development

### Setup

1. Copy the local environment file:

```bash
cp .env.example .env
```

2. Install dependencies (using `uv`):

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

## Database Migrations

Apply the latest migrations:

```bash
alembic upgrade head
```

Create a new migration when needed:

```bash
alembic revision --autogenerate -m "describe change"
```

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
    "name": "SF Downtown AOI",
    "description": "Simple polygon AOI",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [-122.423, 37.775],
        [-122.412, 37.775],
        [-122.412, 37.784],
        [-122.423, 37.784],
        [-122.423, 37.775]
      ]]
    }
  }'
```

### 5) Optionally list AOIs for a project

If enabled in your local code/version:

```bash
curl -s http://127.0.0.1:8000/v1/projects/<project_id>/aois
```

## API Endpoints

- `GET /health`
- `GET /health/db`
- `POST /v1/projects`
- `GET /v1/projects`
- `GET /v1/projects/{project_id}`
- `PATCH /v1/projects/{project_id}`
- `DELETE /v1/projects/{project_id}`
- `POST /v1/projects/{project_id}/aois`
- `GET /v1/projects/{project_id}/aois`
- `GET /v1/aois/{aoi_id}`
- `PATCH /v1/aois/{aoi_id}`
- `DELETE /v1/aois/{aoi_id}`

## Tests

Run tests locally:

```bash
make test
```

The database tests require the PostGIS container to be running.

## Next Milestone

The next milestone is focused on AOI-centric analysis workflows, including:

- AOI retrieval/listing ergonomics
- Geospatial processing jobs tied to AOIs
- Better project/AOI lifecycle and status tracking
