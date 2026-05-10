.PHONY: test

test:
	uv run pytest

format:
	uv run ruff check --fix src tests
	uv run ruff format src tests

format-check:
	uv run ruff check src tests
	uv run ruff format --check src tests

check: format-check test