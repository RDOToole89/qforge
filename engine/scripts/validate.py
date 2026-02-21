#!/usr/bin/env python3
"""
Quantum Experiment Schema Suite Validation Script (Research-Grade)

Validates all JSON schemas and example payloads using schema_index.json as the source of truth.
Also supports validating produced artifacts and targeted validation for a single schema.

Usage:
    python scripts/validate.py                               # Full validation (schemas + examples)
    python scripts/validate.py --schemas-only                # Schema validation only
    python scripts/validate.py --examples-only               # Example validation only
    python scripts/validate.py --output json                 # JSON output for CI/CD
    python scripts/validate.py --output human                # Human-readable output (default)
    python scripts/validate.py --schema-id experiment_spec   # Validate only one schema (and its examples)
    python scripts/validate.py --examples-version v1         # Select examples version folder
    python scripts/validate.py --artifacts ./artifacts       # Validate all JSON files in artifacts dir
    python scripts/validate.py --fail-fast                   # Stop at first error
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any

try:
    import jsonschema
    from jsonschema import Draft7Validator, RefResolver, validators
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print('Install with: pip install "jsonschema>=4.21" referencing')
    sys.exit(1)


# ---------- Error typing & results containers ----------


class ErrorKind(Enum):
    SCHEMA = auto()
    EXAMPLE = auto()
    INDEX = auto()
    CROSSREF = auto()
    ARTIFACT = auto()


@dataclass
class ValidationError:
    """Individual validation error."""

    file: str
    message: str
    details: str = ""
    kind: ErrorKind = ErrorKind.SCHEMA


@dataclass
class ValidationResults:
    """Complete validation results."""

    success: bool = True
    schemas_total: int = 0
    schemas_valid: int = 0
    examples_total: int = 0
    examples_valid: int = 0
    artifacts_total: int = 0
    artifacts_valid: int = 0
    errors: list[ValidationError] = field(default_factory=list)

    def add_error(
        self,
        file: str,
        message: str,
        details: str = "",
        kind: ErrorKind = ErrorKind.SCHEMA,
        fail_fast: bool = False,
    ):
        """Add a validation error and optionally exit immediately."""
        self.success = False
        self.errors.append(ValidationError(file=file, message=message, details=details, kind=kind))
        if fail_fast:
            raise SystemExit(1)


# ---------- Core schema validator ----------


def _validator_for(schema: dict) -> type[Draft7Validator]:
    """Return the appropriate validator class for the given schema."""
    Validator = validators.validator_for(schema)
    Validator.check_schema(schema)
    return Validator


class SchemaValidator:
    """Validates JSON schemas and builds a resolver registry."""

    def __init__(self, repo_root: Path, fail_fast: bool = False):
        self.repo_root = repo_root
        self.schemas_dir = repo_root / "schemas"
        self.schema_registry: dict[str, Any] = {}  # key: schema_id or relative path string
        self.schema_paths: dict[str, Path] = {}  # key: schema_id -> path
        self.schema_index: dict[str, Any] = {}
        self.fail_fast = fail_fast

    def load_schema_index(self) -> bool:
        """Load schema_index.json; basic sanity checks."""
        index_path = self.schemas_dir / "schema_index.json"
        if not index_path.exists():
            print(f"❌ Schema index not found: {index_path}")
            return False

        try:
            with open(index_path, encoding="utf-8") as f:
                self.schema_index = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"❌ Failed to load schema index: {e}")
            return False

        # Basic structure check
        if not isinstance(self.schema_index, dict) or "schemas" not in self.schema_index:
            print("❌ schema_index.json missing 'schemas' array")
            return False

        return True

    def validate_schemas(
        self, results: ValidationResults, only_schema_id: str | None = None
    ) -> bool:
        """Validate all schemas listed in schema_index.json (or a single schema)."""
        if not self.schema_index:
            results.add_error(
                "schema_index.json",
                "Schema index not loaded",
                kind=ErrorKind.INDEX,
                fail_fast=self.fail_fast,
            )
            return False

        schemas = self.schema_index.get("schemas", [])
        if only_schema_id:
            schemas = [s for s in schemas if s.get("id") == only_schema_id]

        results.schemas_total = len(schemas)
        schema_ids: set[str] = set()

        for schema_info in schemas:
            schema_id = schema_info.get("id")
            schema_file = schema_info.get("file")

            if not schema_id or not schema_file:
                results.add_error(
                    "schema_index.json",
                    f"Invalid schema entry: {schema_info}",
                    kind=ErrorKind.INDEX,
                    fail_fast=self.fail_fast,
                )
                continue

            if schema_id in schema_ids:
                results.add_error(
                    "schema_index.json",
                    f"Duplicate schema ID: {schema_id}",
                    kind=ErrorKind.INDEX,
                    fail_fast=self.fail_fast,
                )
                continue
            schema_ids.add(schema_id)

            schema_path = self.schemas_dir / schema_file
            if not schema_path.exists():
                results.add_error(
                    str(schema_path),
                    "Schema file not found",
                    kind=ErrorKind.SCHEMA,
                    fail_fast=self.fail_fast,
                )
                continue

            try:
                with open(schema_path, encoding="utf-8") as f:
                    schema = json.load(f)

                # Validate schema syntax
                _ = _validator_for(schema)  # raises if invalid

                # $id check: allow URIs that end with the basename
                schema_dollar_id = schema.get("$id")
                if schema_dollar_id:
                    expected_basename = schema_path.name
                    if not (
                        schema_dollar_id == expected_basename
                        or schema_dollar_id.endswith("/" + expected_basename)
                    ):
                        results.add_error(
                            str(schema_path),
                            f"$id mismatch: expected basename '{expected_basename}' "
                            f"(or URI ending with it), got '{schema_dollar_id}'",
                            kind=ErrorKind.SCHEMA,
                            fail_fast=self.fail_fast,
                        )

                # Store by logical id
                self.schema_registry[schema_id] = schema
                self.schema_paths[schema_id] = schema_path
                # Store by relative path (string) to support $ref resolution by path
                relative_path = schema_path.relative_to(self.schemas_dir)
                self.schema_registry[str(relative_path)] = schema

                results.schemas_valid += 1

            except json.JSONDecodeError as e:
                results.add_error(
                    str(schema_path),
                    f"Invalid JSON: {e}",
                    kind=ErrorKind.SCHEMA,
                    fail_fast=self.fail_fast,
                )
            except jsonschema.SchemaError as e:
                results.add_error(
                    str(schema_path),
                    f"Invalid JSON Schema: {e}",
                    kind=ErrorKind.SCHEMA,
                    fail_fast=self.fail_fast,
                )
            except Exception as e:
                results.add_error(
                    str(schema_path),
                    f"Error loading schema: {e}",
                    kind=ErrorKind.SCHEMA,
                    fail_fast=self.fail_fast,
                )

        return results.schemas_valid > 0

    def _find_refs(self, obj: Any, path: str = "") -> list[tuple[str, str]]:
        """Recursively find all $ref occurrences in a JSON object."""
        refs: list[tuple[str, str]] = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "$ref" and isinstance(value, str):
                    refs.append((path + ".$ref" if path else "$ref", value))
                else:
                    child_path = f"{path}.{key}" if path else key
                    refs.extend(self._find_refs(value, child_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                child_path = f"{path}[{i}]"
                refs.extend(self._find_refs(item, child_path))
        return refs

    def validate_cross_references(
        self, results: ValidationResults, only_schema_id: str | None = None
    ):
        """Validate that all external $ref in registered schemas resolve and target a registered schema."""
        # Build a quick lookup of relative paths we consider "registered"
        registered_relpaths: set[str] = set()
        for _sid, path in self.schema_paths.items():
            try:
                rel = path.relative_to(self.schemas_dir)
                registered_relpaths.add(str(rel))
            except Exception:
                # Non-relative, ignore
                pass

        for sid, schema in list(self.schema_registry.items()):
            # Skip entries that are already stored by relative path, validate by logical id only:
            if sid not in self.schema_paths:
                continue
            if only_schema_id and sid != only_schema_id:
                continue

            schema_path = self.schema_paths.get(sid)
            if not schema_path:
                continue

            refs = self._find_refs(schema)
            for ref_path, ref_target in refs:
                if ref_target.startswith("#"):
                    # internal anchor: jsonschema already verifies anchors on use; skip explicit check
                    continue

                if ref_target.startswith("http://") or ref_target.startswith("https://"):
                    # External reference over HTTP(S) is out of scope. Warn as crossref if not desired.
                    # For strict local-only suites, treat as an error:
                    results.add_error(
                        str(schema_path),
                        f"External $ref not allowed in this suite: {ref_target}",
                        details=f"At {ref_path}",
                        kind=ErrorKind.CROSSREF,
                        fail_fast=self.fail_fast,
                    )
                    continue

                if ref_target.startswith("../") or ref_target.startswith("./"):
                    # Resolve relative to the current schema file
                    resolved_path = (schema_path.parent / ref_target).resolve()
                    if not resolved_path.exists():
                        results.add_error(
                            str(schema_path),
                            f"Unresolved $ref: {ref_target}",
                            details=f"Path {ref_path} resolves to non-existent {resolved_path}",
                            kind=ErrorKind.CROSSREF,
                            fail_fast=self.fail_fast,
                        )
                        continue
                    try:
                        rel_from_root = resolved_path.relative_to(self.schemas_dir)
                        if str(rel_from_root) not in registered_relpaths:
                            results.add_error(
                                str(schema_path),
                                f"Referenced schema not registered: {resolved_path}",
                                details=f"Add it to schema_index.json or fix $ref at {ref_path}",
                                kind=ErrorKind.CROSSREF,
                                fail_fast=self.fail_fast,
                            )
                    except Exception:
                        # outside schemas dir
                        results.add_error(
                            str(schema_path),
                            f"$ref points outside schemas directory: {resolved_path}",
                            details=f"Ref at {ref_path}",
                            kind=ErrorKind.CROSSREF,
                            fail_fast=self.fail_fast,
                        )
                else:
                    # Try to match against registry by relative path string or logical id
                    if ref_target not in self.schema_registry:
                        results.add_error(
                            str(schema_path),
                            f"Unresolved $ref: {ref_target}",
                            details=f"Reference at {ref_path} not found in registry",
                            kind=ErrorKind.CROSSREF,
                            fail_fast=self.fail_fast,
                        )

    def create_resolver(self) -> RefResolver:
        """Create a JSON Schema resolver backed by our local store."""
        store: dict[str, Any] = {}

        for sid, schema in self.schema_registry.items():
            if isinstance(sid, str):
                # If we have a path for this logical id, include by URI and relative string
                schema_path = self.schema_paths.get(sid)
                if schema_path:
                    store[schema_path.as_uri()] = schema
                    try:
                        rel = str(schema_path.relative_to(self.schemas_dir))
                        store[rel] = schema
                    except Exception:
                        pass
        # Base at the schemas dir so relative $ref work
        resolver = RefResolver(base_uri=self.schemas_dir.as_uri() + "/", referrer={}, store=store)
        return resolver


# ---------- Example validator ----------


class ExampleValidator:
    """Validates example JSON files against their schemas."""

    def __init__(
        self,
        repo_root: Path,
        schema_validator: SchemaValidator,
        version: str = "v1",
        fail_fast: bool = False,
    ):
        self.repo_root = repo_root
        self.examples_dir = repo_root / "schemas" / "examples" / version
        self.schema_validator = schema_validator
        self.version = version
        self.fail_fast = fail_fast

    def validate_examples(
        self,
        results: ValidationResults,
        valid_only: bool = False,
        only_schema_id: str | None = None,
    ):
        """Validate all example files under examples/{version}/{valid|invalid}."""
        if not self.examples_dir.exists():
            results.add_error(
                str(self.examples_dir),
                "Examples directory not found",
                kind=ErrorKind.EXAMPLE,
                fail_fast=self.fail_fast,
            )
            return

        resolver = self.schema_validator.create_resolver()

        def _validate_examples_in_dir(ex_dir: Path, should_be_valid: bool):
            for example_file in sorted(ex_dir.glob("*.json")):
                # If targeting one schema id, skip others by filename convention
                schema_id = self._extract_schema_id(example_file.name)
                if only_schema_id and schema_id != only_schema_id:
                    continue

                results.examples_total += 1

                schema = self.schema_validator.schema_registry.get(schema_id)
                if not schema:
                    results.add_error(
                        str(example_file),
                        f"Schema not found for ID: {schema_id}",
                        kind=ErrorKind.EXAMPLE,
                        fail_fast=self.fail_fast,
                    )
                    continue

                try:
                    with open(example_file, encoding="utf-8") as f:
                        example_data = json.load(f)

                    Validator = _validator_for(schema)
                    validator = Validator(schema, resolver=resolver)
                    errors = list(validator.iter_errors(example_data))

                    if should_be_valid:
                        if errors:
                            error_details: list[str] = []
                            for error in errors[:5]:
                                path = " -> ".join(str(p) for p in error.absolute_path) or "root"
                                error_details.append(f"Path '{path}': {error.message}")
                            if len(errors) > 5:
                                error_details.append(f"... and {len(errors) - 5} more errors")
                            results.add_error(
                                str(example_file),
                                "Valid example failed validation",
                                "; ".join(error_details),
                                kind=ErrorKind.EXAMPLE,
                                fail_fast=self.fail_fast,
                            )
                        else:
                            results.examples_valid += 1
                    else:
                        # Should be invalid
                        if not errors:
                            results.add_error(
                                str(example_file),
                                "Invalid example passed validation (should have failed)",
                                kind=ErrorKind.EXAMPLE,
                                fail_fast=self.fail_fast,
                            )
                        else:
                            results.examples_valid += 1  # Correctly rejected

                except json.JSONDecodeError as e:
                    results.add_error(
                        str(example_file),
                        f"Invalid JSON: {e}",
                        kind=ErrorKind.EXAMPLE,
                        fail_fast=self.fail_fast,
                    )
                except Exception as e:
                    results.add_error(
                        str(example_file),
                        f"Error validating example: {e}",
                        kind=ErrorKind.EXAMPLE,
                        fail_fast=self.fail_fast,
                    )

        valid_dir = self.examples_dir / "valid"
        invalid_dir = self.examples_dir / "invalid"

        if valid_dir.exists():
            _validate_examples_in_dir(valid_dir, should_be_valid=True)
        if not valid_only and invalid_dir.exists():
            _validate_examples_in_dir(invalid_dir, should_be_valid=False)

    @staticmethod
    def _extract_schema_id(filename: str) -> str | None:
        """Extract schema ID from example filename: {schema_id}.{valid|invalid}.json"""
        parts = filename.split(".")
        if len(parts) >= 3 and parts[-1] == "json":
            return parts[0]
        return None


# ---------- Artifacts validator (produced by pipelines) ----------


def validate_artifacts_directory(
    artifacts_dir: Path,
    schema_validator: SchemaValidator,
    results: ValidationResults,
    only_schema_id: str | None = None,
    fail_fast: bool = False,
) -> None:
    """
    Validate all *.json files in artifacts_dir. Each artifact must validate against
    at least one registered schema (or a targeted schema if only_schema_id is provided).
    """
    if not artifacts_dir.exists():
        results.add_error(
            str(artifacts_dir),
            "Artifacts directory not found",
            kind=ErrorKind.ARTIFACT,
            fail_fast=fail_fast,
        )
        return

    resolver = schema_validator.create_resolver()

    # Choose candidate schemas:
    candidate_items: Iterable[tuple[str, dict]] = schema_validator.schema_registry.items()
    if only_schema_id:
        if only_schema_id not in schema_validator.schema_registry:
            results.add_error(
                str(artifacts_dir),
                f"--schema-id '{only_schema_id}' not registered; cannot validate artifacts",
                kind=ErrorKind.ARTIFACT,
                fail_fast=fail_fast,
            )
            return
        candidate_items = [(only_schema_id, schema_validator.schema_registry[only_schema_id])]

    for artifact in sorted(artifacts_dir.glob("*.json")):
        results.artifacts_total += 1
        try:
            with open(artifact, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            results.add_error(
                str(artifact),
                f"Invalid JSON: {e}",
                kind=ErrorKind.ARTIFACT,
                fail_fast=fail_fast,
            )
            continue
        except Exception as e:
            results.add_error(
                str(artifact),
                f"Error reading file: {e}",
                kind=ErrorKind.ARTIFACT,
                fail_fast=fail_fast,
            )
            continue

        # Try all candidate schemas until one passes
        validated = False
        last_errors: list[str] = []
        for sid, schema in candidate_items:
            try:
                Validator = _validator_for(schema)
                validator = Validator(schema, resolver=resolver)
                errs = list(validator.iter_errors(data))
                if not errs:
                    validated = True
                    break
                else:
                    if len(last_errors) < 5:
                        # Collect a few messages for debugging
                        for e in errs[:3]:
                            path = " -> ".join(str(p) for p in e.absolute_path) or "root"
                            last_errors.append(f"[{sid}] {path}: {e.message}")
            except Exception as e:
                last_errors.append(f"[{sid}] validator error: {e}")

        if validated:
            results.artifacts_valid += 1
        else:
            details = "; ".join(last_errors) if last_errors else "No schema matched."
            results.add_error(
                str(artifact),
                "Artifact failed validation against all candidate schemas",
                details=details,
                kind=ErrorKind.ARTIFACT,
                fail_fast=fail_fast,
            )


# ---------- Output formatting ----------


def print_human_results(results: ValidationResults) -> None:
    """Print human-readable validation results."""
    print("\n🔍 Quantum Experiment Schema Suite Validation")
    print("=" * 54)

    print(f"📋 Schemas:  {results.schemas_valid}/{results.schemas_total} valid")
    print(f"📄 Examples:  {results.examples_valid}/{results.examples_total} valid")
    if results.artifacts_total:
        print(f"🧪 Artifacts: {results.artifacts_valid}/{results.artifacts_total} valid")

    if results.success:
        print("\n✅ All validations passed!")
        return

    print("\n❌ Validation errors:")

    by_kind: dict[ErrorKind, int] = {k: 0 for k in ErrorKind}
    for e in results.errors:
        by_kind[e.kind] += 1

    for kind in ErrorKind:
        if by_kind[kind]:
            print(f"  - {kind.name.lower()}: {by_kind[kind]}")

    for error in results.errors:
        print(f"   • [{error.kind.name.lower()}] {error.file}: {error.message}")
        if error.details:
            print(f"     Details: {error.details}")


def print_json_results(results: ValidationResults) -> None:
    """Print JSON validation results for CI/CD."""
    by_kind: dict[str, int] = {}
    for k in ErrorKind:
        by_kind[k.name.lower()] = sum(1 for e in results.errors if e.kind == k)

    output = {
        "success": results.success,
        "schemas": {
            "total": results.schemas_total,
            "valid": results.schemas_valid,
        },
        "examples": {
            "total": results.examples_total,
            "valid": results.examples_valid,
        },
        "artifacts": {
            "total": results.artifacts_total,
            "valid": results.artifacts_valid,
        },
        "errors_by_kind": by_kind,
        "errors": [
            {
                "file": e.file,
                "message": e.message,
                "details": e.details,
                "kind": e.kind.name.lower(),
            }
            for e in results.errors
        ],
    }
    print(json.dumps(output, indent=2))


# ---------- CLI entrypoint ----------


def main() -> None:
    """Main validation entry point."""
    parser = argparse.ArgumentParser(description="Validate Quantum Experiment Schema Suite")
    parser.add_argument("--schemas-only", action="store_true", help="Validate schemas only")
    parser.add_argument("--examples-only", action="store_true", help="Validate examples only")
    parser.add_argument(
        "--output",
        choices=["human", "json"],
        default="human",
        help="Output format (default: human)",
    )
    parser.add_argument("--path", type=Path, default=".", help="Repository root path")
    parser.add_argument(
        "--schema-id", type=str, help="Validate a single schema id (and its examples)"
    )
    parser.add_argument(
        "--examples-version",
        type=str,
        default="v1",
        help="Examples version folder (default v1)",
    )
    parser.add_argument(
        "--artifacts",
        type=Path,
        help="Validate all JSON files in this artifacts directory",
    )
    parser.add_argument("--fail-fast", action="store_true", help="Stop at first error")

    args = parser.parse_args()

    repo_root = args.path.resolve()
    if not repo_root.exists():
        print(f"❌ Repository path does not exist: {repo_root}")
        sys.exit(1)

    results = ValidationResults()

    try:
        # Initialize validator
        schema_validator = SchemaValidator(repo_root, fail_fast=args.fail_fast)

        # Load schema index
        if not schema_validator.load_schema_index():
            sys.exit(1)

        # Validate schemas
        if not args.examples_only:
            schema_validator.validate_schemas(results, only_schema_id=args.schema_id)
            schema_validator.validate_cross_references(results, only_schema_id=args.schema_id)

        # Validate examples
        if not args.schemas_only:
            example_validator = ExampleValidator(
                repo_root,
                schema_validator,
                version=args.examples_version,
                fail_fast=args.fail_fast,
            )
            example_validator.validate_examples(
                results, valid_only=False, only_schema_id=args.schema_id
            )

        # Validate artifacts (if provided)
        if args.artifacts:
            validate_artifacts_directory(
                args.artifacts,
                schema_validator,
                results,
                only_schema_id=args.schema_id,
                fail_fast=args.fail_fast,
            )

        # Output results
        if args.output == "json":
            print_json_results(results)
        else:
            print_human_results(results)

        # Exit code
        sys.exit(0 if results.success else 1)

    except SystemExit as e:
        # allow fail-fast to exit cleanly with code 1
        sys.exit(e.code)
    except Exception as e:
        if args.output == "json":
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
