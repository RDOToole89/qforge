"""Exact-value tests for INTERMEDIARY math helpers in ``src/qforge/core/analysis/core``.

These helpers are exercised by higher-level code but their numeric outputs were
never directly asserted. Every value below was confirmed by running the code and
locking the result. Optimizer / seed-dependent values are marked
``# regression-locked``.

Run (avoiding the repo coverage plugin):
    pytest tests/core/test_math_intermediates_verified.py
"""

from __future__ import annotations

import numpy as np
import pytest

from qforge.core.analysis.core.bootstrap import (
    _compute_bca_interval,
    _compute_bias_correction,
    bootstrap_confidence_interval,
)
from qforge.core.analysis.core.null_models import ghz_aware_null_model
from tests._qhelpers import fraction_ones_q0 as _fraction_ones_q0

# ---------------------------------------------------------------------------
# null_models.ghz_aware_null_model
# ---------------------------------------------------------------------------


class TestGHZAwareNullIntermediates:
    def test_special_and_uniform_other_masses(self):
        null = ghz_aware_null_model({"000": 400, "111": 400, "010": 200})

        # All-zeros and all-ones share the (smoothed) special mass equally.
        assert null["000"] == pytest.approx(0.39865537848605576, abs=1e-15)
        assert null["111"] == pytest.approx(0.39865537848605576, abs=1e-15)
        assert null["000"] == pytest.approx(null["111"], abs=1e-15)

        # Every other outcome shares the same uniformly-distributed remainder.
        uniform_other = 0.03378154050464808
        for bs in null:
            if bs in ("000", "111"):
                continue
            assert null[bs] == pytest.approx(uniform_other, abs=1e-15)

        # Full 2^n support, normalized.
        assert len(null) == 8
        assert sum(null.values()) == pytest.approx(1.0, abs=1e-12)


# ---------------------------------------------------------------------------
# bootstrap.bootstrap_confidence_interval (percentile endpoints)
# ---------------------------------------------------------------------------


class TestBootstrapPercentileEndpoints:
    def test_fixed_seed_percentile_ci(self):
        counts = {"00": 500, "11": 500}
        lo, hi = bootstrap_confidence_interval(
            counts,
            _fraction_ones_q0,
            n_bootstrap=200,
            rng=np.random.default_rng(42),
        )
        # regression-locked (fixed seed=42, B=200, percentile method)
        assert lo == pytest.approx(0.472975, abs=1e-12)
        assert hi == pytest.approx(0.5310750000000001, abs=1e-12)
        assert lo <= 0.5 <= hi


# ---------------------------------------------------------------------------
# bootstrap BCa path: _compute_bias_correction + _compute_bca_interval
# ---------------------------------------------------------------------------


class TestBCaIntermediates:
    def test_symmetric_bias_correction_is_zero(self):
        # Half the resamples strictly below the estimate -> proportion_less = 0.5
        # -> z0 = Phi^-1(0.5) = 0 exactly.
        boot = np.array([0.0] * 100 + [1.0] * 100, dtype=float)
        z0 = _compute_bias_correction(boot, 0.5)
        assert z0 == pytest.approx(0.0, abs=1e-12)

    def test_bca_interval_symmetric_case(self):
        boot = np.array([0.0] * 100 + [1.0] * 100, dtype=float)
        lo, hi = _compute_bca_interval(boot, 0.5, 0.95)
        # With z0 == 0 and a == 0 the adjusted percentiles collapse to the
        # standard 2.5 / 97.5 quantiles of this two-mass distribution.
        assert lo <= hi
        assert lo == pytest.approx(0.0, abs=1e-12)
        assert hi == pytest.approx(1.0, abs=1e-12)

    def test_bca_bias_correction_skewed_sign(self):
        # Most resamples below the estimate -> positive z0 (sanity on direction).
        boot = np.array([0.0] * 180 + [1.0] * 20, dtype=float)
        z0 = _compute_bias_correction(boot, 0.5)
        assert z0 > 0.0
