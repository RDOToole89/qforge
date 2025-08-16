.PHONY: install validate validate-schemas validate-examples clean

# Install validation dependencies
install:
	pip install jsonschema referencing

# Full validation
validate:
	python scripts/validate.py --path .

# Schema validation only
validate-schemas:
	python scripts/validate.py --schemas-only --path .

# Example validation only
validate-examples:
	python scripts/validate.py --examples-only --path .

# JSON output for CI/CD
validate-json:
	python scripts/validate.py --output json --path .

# Clean up temporary files
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete