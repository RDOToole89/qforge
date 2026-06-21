.PHONY: install sync validate validate-schemas validate-examples clean lint format typecheck test check pre-commit

# ── Environment ──────────────────────────────────────────

# One-command setup for collaborators: creates .venv from uv.lock
install sync:
	uv sync

# ── Schema Validation ────────────────────────────────────

validate:
	uv run python scripts/validate.py --path .

validate-schemas:
	uv run python scripts/validate.py --schemas-only --path .

validate-examples:
	uv run python scripts/validate.py --examples-only --path .

validate-json:
	uv run python scripts/validate.py --output json --path .

# ── Development ──────────────────────────────────────────

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests
	uv run ruff check --fix src tests

typecheck:
	uv run mypy src --ignore-missing-imports

test:
	uv run pytest

check: lint typecheck test

pre-commit:
	uv run pre-commit install
	uv run pre-commit run --all-files

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
