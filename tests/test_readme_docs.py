from pathlib import Path

README_PATH = Path(__file__).resolve().parents[1] / "README.md"


def read_readme() -> str:
    return README_PATH.read_text(encoding="utf-8")


def test_readme_includes_setup_and_migration_steps() -> None:
    readme = read_readme()

    assert "## Local Development" in readme
    assert "docker compose up --build" in readme
    assert "docker compose down -v" in readme

    assert "uv run alembic current" in readme
    assert "uv run alembic upgrade head" in readme
    assert 'uv run alembic revision --autogenerate -m "describe change"' in readme
    assert "uv run alembic check" in readme


def test_readme_includes_seed_data_workflow() -> None:
    readme = read_readme()

    assert "## Seed Data" in readme
    assert "uv run python scripts/seed_land_use.py" in readme
    assert "land_use" in readme
    assert "forest" in readme
    assert "agriculture" in readme
    assert "urban" in readme
    assert "water" in readme
    assert "grassland" in readme


def test_readme_includes_required_demo_flow() -> None:
    readme = read_readme()

    assert "curl -s http://127.0.0.1:8000/health" in readme
    assert "curl -s http://127.0.0.1:8000/health/db" in readme

    assert "POST http://127.0.0.1:8000/v1/projects" in readme
    assert "curl -s http://127.0.0.1:8000/v1/projects" in readme

    assert "POST http://127.0.0.1:8000/v1/projects/<project_id>/aois" in readme
    assert "curl -s http://127.0.0.1:8000/v1/projects/<project_id>/aois" in readme

    assert "curl -s http://127.0.0.1:8000/v1/vector-layers" in readme
    assert "POST http://127.0.0.1:8000/v1/aois/<aoi_id>/land-use-composition" in readme


def test_readme_lists_current_api_endpoints() -> None:
    readme = read_readme()

    expected_endpoints = [
        "GET /health",
        "GET /health/db",
        "POST /v1/projects",
        "GET /v1/projects",
        "GET /v1/projects/{project_id}",
        "PATCH /v1/projects/{project_id}",
        "DELETE /v1/projects/{project_id}",
        "POST /v1/projects/{project_id}/aois",
        "GET /v1/projects/{project_id}/aois",
        "GET /v1/aois/{aoi_id}",
        "PATCH /v1/aois/{aoi_id}",
        "DELETE /v1/aois/{aoi_id}",
        "POST /v1/vector-layers",
        "GET /v1/vector-layers",
        "GET /v1/vector-layers/{layer_id}",
        "DELETE /v1/vector-layers/{layer_id}",
        "POST /v1/aois/{aoi_id}/land-use-composition",
    ]

    for endpoint in expected_endpoints:
        assert endpoint in readme


def test_readme_describes_scope_and_next_milestone() -> None:
    readme = read_readme()

    assert "## Current Scope" in readme
    assert "Project CRUD" in readme
    assert "AOI CRUD" in readme
    assert "Vector layer metadata CRUD" in readme
    assert "Land-use composition analysis by AOI using PostGIS" in readme

    assert "## Next Milestone" in readme
    assert "result detail endpoint" in readme
    assert "AOI-level result listing endpoint" in readme
    assert "stronger spatial correctness tests" in readme


def test_readme_uses_uv_commands_instead_of_missing_makefile_commands() -> None:
    readme = read_readme()

    assert "uv run pytest" in readme
    assert "uv run ruff format ." in readme
    assert "uv run ruff check . --fix" in readme

    assert "make test" not in readme
    assert "make format" not in readme
    assert "make format-all" not in readme