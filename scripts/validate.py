#!/usr/bin/env python3
"""
Quantum Experiment Schema Suite Validation Script

Validates all JSON schemas and examples using schema_index.json as source of truth.
Production-ready validation pipeline for CI/CD integration.

Usage:
    python scripts/validate.py                     # Full validation
    python scripts/validate.py --schemas-only      # Schema validation only
    python scripts/validate.py --examples-only     # Example validation only
    python scripts/validate.py --output json       # JSON output for CI/CD
    python scripts/validate.py --output human      # Human-readable output (default)
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

try:
    import jsonschema
    from jsonschema import Draft7Validator, RefResolver
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print("Install with: pip install jsonschema referencing")
    sys.exit(1)


@dataclass
class ValidationError:
    """Individual validation error."""
    file: str
    message: str
    details: str = ""


@dataclass
class ValidationResults:
    """Complete validation results."""
    success: bool = True
    schemas_total: int = 0
    schemas_valid: int = 0
    examples_total: int = 0
    examples_valid: int = 0
    errors: List[ValidationError] = field(default_factory=list)
    
    def add_error(self, file: str, message: str, details: str = ""):
        """Add a validation error."""
        self.success = False
        self.errors.append(ValidationError(file=file, message=message, details=details))


class SchemaValidator:
    """Validates JSON schemas and builds resolver registry."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.schemas_dir = repo_root / "schemas"
        self.schema_registry: Dict[str, Any] = {}
        self.schema_paths: Dict[str, Path] = {}
        self.schema_index: Dict[str, Any] = {}
        
    def load_schema_index(self) -> bool:
        """Load and validate schema_index.json."""
        index_path = self.schemas_dir / "schema_index.json"
        if not index_path.exists():
            print(f"❌ Schema index not found: {index_path}")
            return False
            
        try:
            with open(index_path, 'r') as f:
                self.schema_index = json.load(f)
            return True
        except (json.JSONDecodeError, Exception) as e:
            print(f"❌ Failed to load schema index: {e}")
            return False
    
    def validate_schemas(self, results: ValidationResults) -> bool:
        """Validate all schemas listed in schema_index.json."""
        if not self.schema_index:
            results.add_error("schema_index.json", "Schema index not loaded")
            return False
            
        schemas = self.schema_index.get("schemas", [])
        results.schemas_total = len(schemas)
        schema_ids: Set[str] = set()
        
        for schema_info in schemas:
            schema_id = schema_info.get("id")
            schema_file = schema_info.get("file")
            
            if not schema_id or not schema_file:
                results.add_error("schema_index.json", f"Invalid schema entry: {schema_info}")
                continue
                
            # Check for duplicate IDs
            if schema_id in schema_ids:
                results.add_error("schema_index.json", f"Duplicate schema ID: {schema_id}")
                continue
            schema_ids.add(schema_id)
            
            # Load and validate schema file
            schema_path = self.schemas_dir / schema_file
            if not schema_path.exists():
                results.add_error(str(schema_path), "Schema file not found")
                continue
                
            try:
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                    
                # Validate schema syntax
                Draft7Validator.check_schema(schema)
                
                # Check $id matches expected
                schema_dollar_id = schema.get("$id")
                if schema_dollar_id and schema_dollar_id != f"{schema_path.name}":
                    results.add_error(
                        str(schema_path), 
                        f"$id mismatch: expected {schema_path.name}, got {schema_dollar_id}"
                    )
                
                # Store in registry
                self.schema_registry[schema_id] = schema
                self.schema_paths[schema_id] = schema_path
                
                # Store by file path for resolver
                relative_path = schema_path.relative_to(self.schemas_dir)
                self.schema_registry[str(relative_path)] = schema
                
                results.schemas_valid += 1
                
            except json.JSONDecodeError as e:
                results.add_error(str(schema_path), f"Invalid JSON: {e}")
            except jsonschema.SchemaError as e:
                results.add_error(str(schema_path), f"Invalid JSON Schema: {e}")
            except Exception as e:
                results.add_error(str(schema_path), f"Error loading schema: {e}")
        
        return results.schemas_valid > 0
    
    def validate_cross_references(self, results: ValidationResults):
        """Validate all $ref cross-references resolve correctly."""
        
        def find_refs(obj, path=""):
            """Recursively find all $ref in schema."""
            refs = []
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == '$ref':
                        refs.append((path + '.$ref', value))
                    else:
                        refs.extend(find_refs(value, path + '.' + key if path else key))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    refs.extend(find_refs(item, path + f'[{i}]'))
            return refs
        
        for schema_id, schema in self.schema_registry.items():
            if isinstance(schema_id, Path):  # Skip path-based entries
                continue
                
            refs = find_refs(schema)
            schema_path = self.schema_paths.get(schema_id)
            
            for ref_path, ref_target in refs:
                if ref_target.startswith('#'):
                    # Internal reference - assume valid for now
                    continue
                    
                # External reference - check if it resolves
                if ref_target.startswith('../'):
                    # Relative path from current schema
                    if schema_path:
                        resolved_path = (schema_path.parent / ref_target).resolve()
                        if not resolved_path.exists():
                            results.add_error(
                                str(schema_path),
                                f"Unresolved $ref: {ref_target}",
                                f"Path {ref_path} points to non-existent {resolved_path}"
                            )
                else:
                    # Direct schema file reference
                    if ref_target not in self.schema_registry:
                        results.add_error(
                            str(schema_path) if schema_path else schema_id,
                            f"Unresolved $ref: {ref_target}",
                            f"Reference at {ref_path} not found in schema registry"
                        )
    
    def create_resolver(self) -> RefResolver:
        """Create JSONSchema resolver with all schemas."""
        store = {}
        
        # Add schemas to store by various keys
        for schema_id, schema in self.schema_registry.items():
            if isinstance(schema_id, str) and not isinstance(schema_id, Path):
                # Add by schema ID
                store[f"#{schema_id}"] = schema
                
                # Add by file URI if we have path
                schema_path = self.schema_paths.get(schema_id)
                if schema_path:
                    store[schema_path.as_uri()] = schema
                    # Add by relative path
                    rel_path = schema_path.relative_to(self.schemas_dir)
                    store[str(rel_path)] = schema
        
        # Create resolver with base URI pointing to schemas directory
        resolver = RefResolver(
            base_uri=self.schemas_dir.as_uri() + "/",
            referrer={},
            store=store
        )
        return resolver


class ExampleValidator:
    """Validates example JSON files against their schemas."""
    
    def __init__(self, repo_root: Path, schema_validator: SchemaValidator, version: str = "v1"):
        self.repo_root = repo_root
        self.examples_dir = repo_root / "schemas" / "examples" / version
        self.schema_validator = schema_validator
        self.version = version
        
    def validate_examples(self, results: ValidationResults, valid_only: bool = False):
        """Validate all example files."""
        if not self.examples_dir.exists():
            results.add_error(str(self.examples_dir), "Examples directory not found")
            return
            
        valid_dir = self.examples_dir / "valid"
        invalid_dir = self.examples_dir / "invalid"
        
        # Validate valid examples
        if valid_dir.exists():
            self._validate_examples_in_dir(valid_dir, results, should_be_valid=True)
            
        # Validate invalid examples (should fail validation)
        if not valid_only and invalid_dir.exists():
            self._validate_examples_in_dir(invalid_dir, results, should_be_valid=False)
    
    def _validate_examples_in_dir(self, examples_dir: Path, results: ValidationResults, should_be_valid: bool):
        """Validate examples in a specific directory."""
        resolver = self.schema_validator.create_resolver()
        
        for example_file in examples_dir.glob("*.json"):
            results.examples_total += 1
            
            # Map example to schema using filename
            schema_id = self._extract_schema_id(example_file.name)
            if not schema_id:
                results.add_error(
                    str(example_file),
                    "Cannot determine schema ID from filename"
                )
                continue
                
            # Get schema
            schema = self.schema_validator.schema_registry.get(schema_id)
            if not schema:
                results.add_error(
                    str(example_file),
                    f"Schema not found for ID: {schema_id}"
                )
                continue
            
            # Load and validate example
            try:
                with open(example_file, 'r') as f:
                    example_data = json.load(f)
                    
                # Validate against schema
                validator = Draft7Validator(schema, resolver=resolver)
                errors = list(validator.iter_errors(example_data))
                
                if should_be_valid:
                    # This should be valid
                    if errors:
                        error_details = []
                        for error in errors[:3]:  # Limit to 3 errors
                            path = ' -> '.join(str(p) for p in error.absolute_path) or 'root'
                            error_details.append(f"Path '{path}': {error.message}")
                        if len(errors) > 3:
                            error_details.append(f"... and {len(errors) - 3} more errors")
                            
                        results.add_error(
                            str(example_file),
                            "Valid example failed validation",
                            '; '.join(error_details)
                        )
                    else:
                        results.examples_valid += 1
                else:
                    # This should be invalid
                    if not errors:
                        results.add_error(
                            str(example_file),
                            "Invalid example passed validation (should have failed)"
                        )
                    else:
                        results.examples_valid += 1  # Successfully invalid
                        
            except json.JSONDecodeError as e:
                results.add_error(str(example_file), f"Invalid JSON: {e}")
            except Exception as e:
                results.add_error(str(example_file), f"Error validating example: {e}")
    
    def _extract_schema_id(self, filename: str) -> Optional[str]:
        """Extract schema ID from example filename."""
        # Format: {schema_id}.{valid|invalid}.json
        parts = filename.split('.')
        if len(parts) >= 3 and parts[-1] == 'json':
            return parts[0]
        return None


def print_human_results(results: ValidationResults):
    """Print human-readable validation results."""
    print()
    print("🔍 Quantum Experiment Schema Suite Validation")
    print("=" * 50)
    
    # Schema results
    if results.schemas_total > 0:
        print(f"📋 Schemas: {results.schemas_valid}/{results.schemas_total} valid")
        schema_errors = [e for e in results.errors if 'schema' in e.file.lower()]
        if schema_errors:
            print(f"   ❌ {len(schema_errors)} schema errors")
    
    # Example results
    if results.examples_total > 0:
        print(f"📄 Examples: {results.examples_valid}/{results.examples_total} valid")
        example_errors = [e for e in results.errors if 'example' in e.file.lower()]
        if example_errors:
            print(f"   ❌ {len(example_errors)} example errors")
    
    # Overall result
    print()
    if results.success:
        print("✅ All validations passed!")
    else:
        print(f"❌ {len(results.errors)} validation errors found:")
        for error in results.errors:
            print(f"   • {error.file}: {error.message}")
            if error.details:
                print(f"     Details: {error.details}")


def print_json_results(results: ValidationResults):
    """Print JSON validation results for CI/CD."""
    output = {
        "success": results.success,
        "schemas": {
            "total": results.schemas_total,
            "valid": results.schemas_valid,
            "errors": len([e for e in results.errors if 'schema' in e.file.lower()])
        },
        "examples": {
            "total": results.examples_total,
            "valid": results.examples_valid,
            "errors": len([e for e in results.errors if 'example' in e.file.lower()])
        },
        "errors": [
            {
                "file": error.file,
                "message": error.message,
                "details": error.details
            }
            for error in results.errors
        ]
    }
    print(json.dumps(output, indent=2))


def main():
    """Main validation entry point."""
    parser = argparse.ArgumentParser(description='Validate Quantum Experiment Schema Suite')
    parser.add_argument('--schemas-only', action='store_true', help='Validate schemas only')
    parser.add_argument('--examples-only', action='store_true', help='Validate examples only')
    parser.add_argument('--output', choices=['human', 'json'], default='human', 
                       help='Output format (default: human)')
    parser.add_argument('--path', type=Path, default='.', help='Repository root path')
    
    args = parser.parse_args()
    
    repo_root = args.path.resolve()
    if not repo_root.exists():
        print(f"❌ Repository path does not exist: {repo_root}")
        sys.exit(1)
    
    results = ValidationResults()
    
    try:
        # Initialize validator
        schema_validator = SchemaValidator(repo_root)
        
        # Load schema index
        if not schema_validator.load_schema_index():
            sys.exit(1)
        
        # Validate schemas
        if not args.examples_only:
            schema_validator.validate_schemas(results)
            schema_validator.validate_cross_references(results)
        
        # Validate examples
        if not args.schemas_only:
            example_validator = ExampleValidator(repo_root, schema_validator, version="v1")
            example_validator.validate_examples(results, valid_only=args.examples_only)
        
        # Output results
        if args.output == 'json':
            print_json_results(results)
        else:
            print_human_results(results)
        
        # Exit with appropriate code
        sys.exit(0 if results.success else 1)
        
    except Exception as e:
        if args.output == 'json':
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()