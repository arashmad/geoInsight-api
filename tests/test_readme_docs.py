from pathlib import Path


README_PATH = Path(__file__).resolve().parents[1] / "README.md"


def test_readme_includes_setup_and_migration_steps() -> None:
    readme = README_PATH.read_text(encoding="utf-8")

    assert "## Local setup" in readme
    assert "docker compose up --build" in readme
    assert "alembic upgrade head" in readme


def test_readme_includes_required_curl_flow() -> None:
    readme = README_PATH.read_text(encoding="utf-8")

    assert "curl -s http://127.0.0.1:8000/health" in readme
    assert "POST http://127.0.0.1:8000/api/v1/projects" in readme
    assert "curl -s http://127.0.0.1:8000/api/v1/projects" in readme
    assert "POST http://127.0.0.1:8000/api/v1/projects/<project_id>/aois" in readme


def test_readme_describes_scope_and_next_milestone() -> None:
    readme = README_PATH.read_text(encoding="utf-8")

    assert "## Current scope" in readme
    assert "## Next milestone" in readme
