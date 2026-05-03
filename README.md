# GeoInsight API

FastAPI backend for geospatial analysis workflows.

## Local development with PostGIS

This project uses PostgreSQL with PostGIS for local development.

1. Create local environment file:

```bash
cp .env.example .env
```

2. Start services:

```bash
docker compose up --build
```

3. API health check:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/health/db
```

4. Stop services:

```bash
docker compose down
```

Database connection is configured via `.env` (see `.env.example`).

## Tests

Run tests locally:

```bash
make test
```

The database tests require the PostGIS container to be running.
