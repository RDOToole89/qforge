"""
Test constants module for validation, type safety, and helper functions.
"""

import pytest
from typing import Mapping

from src.core.analysis.constants import (
    ALPHA,
    CONF_INT_DEFAULT,
    MAX_TOP_K,
    TOPK_MASS_TARGET,
    validate_counts_dict,
    get_status_thresholds,
)


class TestConstants:
    """Test constant values and their properties."""

    def test_alpha_value(self):
        """Test Jeffreys prior constant is 0.5."""
        assert ALPHA == 0.5

    def test_confidence_interval_default(self):
        """Test default confidence interval is (2.5, 97.5)."""
        assert CONF_INT_DEFAULT == (2.5, 97.5)

    def test_topk_constants(self):
        """Test top-k analysis constants."""
        assert isinstance(MAX_TOP_K, int)
        assert MAX_TOP_K > 0
        assert 0.0 < TOPK_MASS_TARGET <= 1.0

    def test_status_thresholds(self):
        """Test status threshold values."""
        thresholds = get_status_thresholds()
        assert isinstance(thresholds, dict)
        # Check for actual keys in the thresholds dict
        assert "validated_cv" in thresholds
        assert "experimental_cv" in thresholds
        assert "experimental_min_samples" in thresholds


class TestValidateCountsDict:
    """Test counts dictionary validation."""

    def test_valid_counts(self):
        """Test valid count dictionary."""
        counts = {"00": 100, "01": 200, "10": 150, "11": 50}
        result = validate_counts_dict(counts)
        assert result == counts

    def test_empty_counts(self):
        """Test empty counts dictionary."""
        counts = {}
        with pytest.raises(ValueError, match="dictionary is empty"):
            validate_counts_dict(counts)

    def test_negative_counts(self):
        """Test negative count values."""
        counts = {"00": 100, "01": -50}
        with pytest.raises(ValueError, match="is not a non-negative integer"):
            validate_counts_dict(counts)

    def test_zero_counts_allowed(self):
        """Test that zero counts are allowed."""
        counts = {"00": 100, "01": 0, "10": 50}
        result = validate_counts_dict(counts)
        assert result == counts

    def test_non_integer_counts(self):
        """Test non-integer count values."""
        counts = {"00": 100.5, "01": 50}
        with pytest.raises(ValueError, match="is not a non-negative integer"):
            validate_counts_dict(counts)

    def test_invalid_bitstring_keys(self):
        """Test invalid bitstring keys."""
        counts = {"00": 100, "012": 50}  # Mixed lengths
        with pytest.raises(ValueError, match="contains bitstrings of inconsistent lengths"):
            validate_counts_dict(counts)

    def test_non_binary_bitstrings(self):
        """Test non-binary characters in bitstrings."""
        counts = {"00": 100, "02": 50}
        with pytest.raises(ValueError, match="contains non-binary bitstring"):
            validate_counts_dict(counts)

    def test_mapping_input(self):
        """Test that Mapping inputs are converted to dict."""
        from collections import OrderedDict
        counts = OrderedDict([("00", 100), ("11", 200)])
        result = validate_counts_dict(counts)
        assert isinstance(result, dict)
        assert result == {"00": 100, "11": 200}

    def test_single_qubit_counts(self):
        """Test single qubit counts validation."""
        counts = {"0": 100, "1": 200}
        result = validate_counts_dict(counts)
        assert result == counts

    def test_three_qubit_counts(self):
        """Test three qubit counts validation."""
        counts = {"000": 100, "001": 50, "111": 200}
        result = validate_counts_dict(counts)
        assert result == counts

    def test_large_counts(self):
        """Test large count values."""
        counts = {"00": 1000000, "11": 2000000}
        result = validate_counts_dict(counts)
        assert result == counts