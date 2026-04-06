.PHONY: install validate validate-schemas validate-examples clean lint format typecheck test check pre-commit

# ── Schema Validation ────────────────────────────────────

install:
	pip install jsonschema referencing

validate:
	python scripts/validate.py --path .

validate-schemas:
	python scripts/validate.py --schemas-only --path .

validate-examples:
	python scripts/validate.py --examples-only --path .

validate-json:
	python scripts/validate.py --output json --path .

# ── Development ──────────────────────────────────────────

lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check --fix src tests

typecheck:
	mypy src --ignore-missing-imports

test:
	pytest

check: lint typecheck test

pre-commit:
	pre-commit install
	pre-commit run --all-files

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
