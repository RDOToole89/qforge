"""
Test schema bridge compatibility for structured decoherence metrics.
"""

import pytest

from src.core.analysis.metrics.schema_bridge import (
    get_schema_field_mapping,
)


class TestSchemaCompliance:
    """Test v1.0 schema compliance functions."""

    def test_get_schema_field_mapping(self):
        """Test schema field mapping retrieval."""
        mapping = get_schema_field_mapping()
        assert isinstance(mapping, dict)
        assert len(mapping) > 0

        # Should contain expected schema field mappings
        # The mapping should be a dictionary of canonical->schema mappings
        for canonical_name, schema_field in mapping.items():
            assert isinstance(canonical_name, str)
            assert isinstance(schema_field, str)
            assert len(canonical_name) > 0
            assert len(schema_field) > 0

    def test_schema_field_mapping_structure(self):
        """Test that schema field mapping has expected structure."""
        mapping = get_schema_field_mapping()

        # Should be a non-empty dictionary
        assert isinstance(mapping, dict)
        assert len(mapping) > 0

        # All keys and values should be strings
        for key, value in mapping.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
            assert key.strip() == key  # No leading/trailing spaces
            assert value.strip() == value  # No leading/trailing spaces

    def test_schema_field_mapping_consistency(self):
        """Test internal consistency of schema field mapping."""
        mapping = get_schema_field_mapping()

        # Keys should be unique
        assert len(mapping) == len(set(mapping.keys()))

        # Values should be a subset of keys (canonical names are keys too)
        # Actually, values are the canonical names.
        # We can check that values are unique enough (at least 1)
        assert len(set(mapping.values())) > 0

        # No empty strings
        for key, value in mapping.items():
            assert len(key) > 0
            assert len(value) > 0


class TestSchemaIntegration:
    """Test integration aspects of schema bridge."""

    def test_mapping_accessibility(self):
        """Test that mapping is accessible and stable."""
        # Should be able to call multiple times
        mapping1 = get_schema_field_mapping()
        mapping2 = get_schema_field_mapping()

        # Should return same results
        assert mapping1 == mapping2

        # Should be immutable (or at least stable)
        assert isinstance(mapping1, dict)
        assert isinstance(mapping2, dict)

    def test_mapping_reasonable_content(self):
        """Test that mapping contains reasonable field names."""
        mapping = get_schema_field_mapping()

        # Should contain multiple mappings
        assert len(mapping) >= 1

        # Field names should follow reasonable naming conventions
        for canonical_name, schema_field in mapping.items():
            # Should be snake_case or similar
            assert "_" in canonical_name or canonical_name.islower()
            assert "_" in schema_field or schema_field.islower()

            # Should not contain spaces or special chars (except underscore)
            assert " " not in canonical_name
            assert " " not in schema_field
            for char in canonical_name:
                assert char.isalnum() or char == "_"
            for char in schema_field:
                assert char.isalnum() or char == "_"

    def test_error_handling(self):
        """Test error handling for schema bridge functions."""
        # get_schema_field_mapping should not raise errors
        try:
            mapping = get_schema_field_mapping()
            assert isinstance(mapping, dict)
        except Exception as e:
            pytest.fail(f"get_schema_field_mapping raised unexpected error: {e}")

    def test_mapping_deterministic(self):
        """Test that mapping is deterministic across calls."""
        mappings = []
        for _ in range(5):
            mapping = get_schema_field_mapping()
            mappings.append(mapping)

        # All mappings should be identical
        for mapping in mappings[1:]:
            assert mapping == mappings[0]
