"""Generate the frontend static catalog from backend sources of truth.

This script makes the Python backend the single source of truth for the static
catalogs that the React Native client would otherwise hardcode. It introspects:

- State types / sim modes / noise types / research types / qubit range:
  the ``ExperimentConfig`` Pydantic model (``src/engine/models/config.py``).
- Metric profiles + individual metric names:
  ``src/core/analysis/metrics/profiles.py`` and the metric registry.
- Named statevectors:
  built with ``src/core/state_preparation`` + Qiskit ``Statevector``.
- Per-state two-qubit correlator signatures:
  ``src/engine/bloch_math.two_qubit_correlators`` on the prepared states.

It emits ``apps/client/src/generated/catalog.ts``.

Basis convention
----------------
The frontend uses qubit 0 = MSB = leftmost bitstring character; Qiskit
statevectors are little-endian (qubit 0 = LSB). Every statevector and density
matrix produced here is converted to the frontend convention via Qiskit's
``reverse_qargs()`` before emission. Global phase is canonicalised so the first
nonzero amplitude is real and positive (global phase is physically irrelevant
and this makes the output byte-stable and comparable to the existing
hand-written frontend arrays).

Run:
    uv run python scripts/gen_frontend_constants.py
    # or
    .venv/Scripts/python.exe scripts/gen_frontend_constants.py
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, get_args, get_origin

import annotated_types as at
import numpy as np
from numpy.typing import NDArray
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace
from typing import Literal

from src.core.analysis.metrics.profiles import METRIC_PROFILES
from src.engine.bloch_math import two_qubit_correlators
from src.engine.models.config import ExperimentConfig
from src.core.state_preparation.state_factory import prepare_state

# Tolerances for cleaning floating-point dust before emission.
_ZERO_TOL = 1e-12
_ROUND_SV = 12
_ROUND_CORR = 6

# State types that cannot be entangled and therefore meaningfully support a
# single qubit in the UI (control baseline). All others get a UI floor of 2.
_PRODUCT_STATES = {"SUPERPOSITION"}

# Named statevectors to build: frontend id -> (state_type, num_qubits, params).
# Keyed by the *frontend* ids used in idealStates.ts so the client can look them
# up directly. Only states the backend can prepare are listed; purely
# pedagogical entries (single-qubit basis states, GHZ-minus, Dicke) have no
# clean backend source and stay local in the frontend.
_NAMED_STATEVECTORS: dict[str, tuple[str, int, dict[str, Any] | None]] = {
    "bell_phi_plus": ("BELL", 2, {"variant": "phi_plus"}),
    "bell_phi_minus": ("BELL", 2, {"variant": "phi_minus"}),
    "bell_psi_plus": ("BELL", 2, {"variant": "psi_plus"}),
    "bell_psi_minus": ("BELL", 2, {"variant": "psi_minus"}),
    "ghz3": ("GHZ", 3, None),
    "w3": ("W", 3, None),
    "ghz4": ("GHZ", 4, None),
    "w4": ("W", 4, None),
    "cluster4_ideal": ("CLUSTER", 4, None),
}

# Per-state two-qubit correlator signatures: bloch-config key -> (state, n).
# GHZ uses n=2 (the entangled-pair signature, identical to a Bell state); this
# matches the existing bloch-sphere config and is the meaningful 2-body
# signature. Others use their canonical sizes.
_CORRELATOR_STATES: dict[str, tuple[str, int]] = {
    "ghz": ("GHZ", 2),
    "bell": ("BELL", 2),
    "w_state": ("W", 3),
    "cluster": ("CLUSTER", 4),
    "superposition": ("SUPERPOSITION", 2),
}

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "apps" / "client" / "src" / "generated" / "catalog.ts"


# --------------------------------------------------------------------------- #
# Backend introspection helpers
# --------------------------------------------------------------------------- #
def _literal_args(annotation: Any) -> list[str]:
    """Extract the Literal members from a (possibly Optional) annotation."""
    if get_origin(annotation) is Literal:
        return list(get_args(annotation))
    for arg in get_args(annotation):
        if get_origin(arg) is Literal:
            return list(get_args(arg))
    raise ValueError(f"No Literal found in annotation: {annotation!r}")


def _field_literals(field_name: str) -> list[str]:
    return _literal_args(ExperimentConfig.model_fields[field_name].annotation)


def _qubit_bounds() -> tuple[int, int]:
    meta = ExperimentConfig.model_fields["num_qubits"].metadata
    ge = le = None
    for m in meta:
        if isinstance(m, at.Ge):
            ge = int(m.ge)
        if isinstance(m, at.Le):
            le = int(m.le)
    assert ge is not None and le is not None
    return ge, le


def _state_qubit_range(state_type: str, lo: int, hi: int) -> tuple[int, int]:
    """Probe the backend for the supported qubit range of a state type.

    Returns (minQubits, maxQubits) capped to the global [lo, hi] range, with a
    UI floor of 2 qubits for entangling states (a single qubit cannot carry the
    entanglement those states represent). Product/control states keep their true
    backend minimum.
    """
    supported = []
    logging.disable(logging.CRITICAL)  # silence expected probe failures
    try:
        for n in range(lo, hi + 1):
            try:
                prepare_state(state_type, n)
                supported.append(n)
            except Exception:
                pass
    finally:
        logging.disable(logging.NOTSET)
    if not supported:
        raise RuntimeError(f"State {state_type} supports no qubit count in [{lo},{hi}]")
    n_min, n_max = min(supported), max(supported)
    if state_type not in _PRODUCT_STATES:
        n_min = max(n_min, 2)
    return n_min, n_max


# --------------------------------------------------------------------------- #
# Quantum math helpers (all output in frontend convention: qubit 0 = MSB)
# --------------------------------------------------------------------------- #
def _canonical_global_phase(vec: NDArray[np.complex128]) -> NDArray[np.complex128]:
    """Multiply by a global phase so the first nonzero amplitude is real > 0."""
    for amp in vec:
        if abs(amp) > _ZERO_TOL:
            return vec * (abs(amp) / amp)
    return vec


def _frontend_statevector(state_type: str, n: int, params: dict | None) -> list[list[float]]:
    qc = prepare_state(state_type, n, custom_params=params)
    sv = np.asarray(Statevector(qc).reverse_qargs().data)  # -> qubit 0 = MSB
    sv = _canonical_global_phase(sv)
    out: list[list[float]] = []
    for amp in sv:
        re = round(float(amp.real), _ROUND_SV)
        im = round(float(amp.imag), _ROUND_SV)
        out.append([re + 0.0, im + 0.0])  # normalise -0.0 -> 0.0
    return out


def _frontend_correlators(state_type: str, n: int) -> dict[str, float]:
    qc = prepare_state(state_type, n)
    dm = DensityMatrix(qc).reverse_qargs()  # -> qubit 0 = MSB
    trace_out = [q for q in range(n) if q not in (0, 1)]
    rho2 = partial_trace(dm, trace_out).data if trace_out else dm.data
    corr = two_qubit_correlators(np.asarray(rho2, dtype=np.complex128))
    return {k: round(v, _ROUND_CORR) + 0.0 for k, v in corr.items()}


# --------------------------------------------------------------------------- #
# TypeScript emission helpers
# --------------------------------------------------------------------------- #
def _num(x: float) -> str:
    """Format a float for TS, dropping the trailing .0 only for clean ints."""
    if x == int(x):
        return str(int(x))
    return repr(x)


def _str_array(items: list[str]) -> str:
    return "[" + ", ".join(f'"{s}"' for s in items) + "]"


def _complex_array(amps: list[list[float]]) -> str:
    return "[" + ", ".join(f"[{_num(re)}, {_num(im)}]" for re, im in amps) + "]"


def _build_ts() -> str:
    lo, hi = _qubit_bounds()

    state_ids = [s for s in _field_literals("state_type") if s != "CUSTOM"]
    sim_modes = _field_literals("sim_mode")
    noise_types = _field_literals("noise_type")
    research_types = _field_literals("research_type")

    # Union of all profile metrics, preserving first-seen order.
    metric_names: list[str] = []
    for metrics in METRIC_PROFILES.values():
        for m in metrics:
            if m not in metric_names:
                metric_names.append(m)

    state_rows = []
    for sid in state_ids:
        n_min, n_max = _state_qubit_range(sid, lo, hi)
        state_rows.append(
            f'  {{ id: "{sid}", minQubits: {n_min}, maxQubits: {n_max} }},'
        )

    profile_rows = [
        f"  {name}: {_str_array(list(metrics))} as readonly string[],"
        for name, metrics in METRIC_PROFILES.items()
    ]

    sv_rows = []
    for fid, (stype, n, params) in _NAMED_STATEVECTORS.items():
        amps = _frontend_statevector(stype, n, params)
        sv_rows.append(
            f'  {fid}: {{ id: "{fid}", numQubits: {n}, '
            f"amplitudes: {_complex_array(amps)} }},"
        )

    corr_rows = []
    for key, (stype, n) in _CORRELATOR_STATES.items():
        c = _frontend_correlators(stype, n)
        body = ", ".join(f"{k}: {_num(c[k])}" for k in ("zi", "iz", "zz", "xx", "yy"))
        corr_rows.append(
            f"  {key}: {{ numQubits: {n}, correlators: {{ {body} }} }},"
        )

    nl = "\n"
    return f"""// AUTO-GENERATED by scripts/gen_frontend_constants.py - DO NOT EDIT. \
Run: uv run python scripts/gen_frontend_constants.py
//
// Single source of truth for backend-owned static catalogs. Purely-UI metadata
// (labels, descriptions, icons, LaTeX, display ordering subsets) lives in the
// feature modules that consume these constants, not here.

/** [real, imaginary] amplitude pair. */
export type Complex = readonly [number, number];

/** Inclusive qubit-count bounds from ExperimentConfig.num_qubits. */
export const QUBIT_MIN = {lo};
export const QUBIT_MAX = {hi};

export interface CatalogStateType {{
  readonly id: string;
  readonly minQubits: number;
  readonly maxQubits: number;
}}

/** Selectable quantum state types (CUSTOM is excluded from the configure UI). */
export const STATE_TYPES: readonly CatalogStateType[] = [
{nl.join(state_rows)}
] as const;

/** Simulation execution modes (ExperimentConfig.sim_mode). */
export const SIM_MODES: readonly string[] = {_str_array(sim_modes)} as const;

/** Noise channel ids (ExperimentConfig.noise_type). */
export const NOISE_TYPES: readonly string[] = {_str_array(noise_types)} as const;

/** Research analysis types (ExperimentConfig.research_type). */
export const RESEARCH_TYPES: readonly string[] = {_str_array(research_types)} as const;

/** Individual metric ids (union of all profile metrics, registry-backed). */
export const METRIC_NAMES: readonly string[] = {_str_array(metric_names)} as const;

/** Named metric profiles -> ordered metric id list. */
export const METRIC_PROFILES: Readonly<Record<string, readonly string[]>> = {{
{nl.join(profile_rows)}
}};

export interface NamedStatevector {{
  readonly id: string;
  readonly numQubits: number;
  /** Amplitudes in frontend basis convention (qubit 0 = MSB = leftmost bit). */
  readonly amplitudes: readonly Complex[];
}}

/**
 * Named statevectors built from the backend state-preparation circuits and
 * Qiskit, converted to the frontend basis convention and canonicalised to a
 * real-positive leading amplitude.
 */
export const NAMED_STATEVECTORS: Readonly<Record<string, NamedStatevector>> = {{
{nl.join(sv_rows)}
}};

export interface CatalogCorrelators {{
  readonly zi: number;
  readonly iz: number;
  readonly zz: number;
  readonly xx: number;
  readonly yy: number;
}}

export interface CatalogStateCorrelators {{
  readonly numQubits: number;
  readonly correlators: CatalogCorrelators;
}}

/**
 * Backend-faithful two-qubit correlator signatures (qubits 0,1 of the prepared
 * state, frontend basis convention) via bloch_math.two_qubit_correlators.
 * GHZ uses n=2 (the entangled-pair signature). These are the mathematically
 * exact reduced-state correlators; the bloch-sphere feature additionally keeps
 * curated/pedagogical signatures local where they intentionally diverge.
 */
export const STATE_CORRELATORS: Readonly<Record<string, CatalogStateCorrelators>> = {{
{nl.join(corr_rows)}
}};
"""


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = _build_ts()
    OUT_PATH.write_text(ts, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT_PATH.relative_to(REPO_ROOT)}")
    _verify_against_ideal_states()


# --------------------------------------------------------------------------- #
# Correctness gate: generated statevectors vs existing idealStates.ts arrays
# --------------------------------------------------------------------------- #
def _verify_against_ideal_states() -> None:
    """Compare generated statevectors against the existing frontend arrays.

    Prints a per-state PASS/FAIL report. Matching is up to canonical global
    phase and a 1e-9 tolerance.
    """
    s2 = 1 / np.sqrt(2)
    s3 = 1 / np.sqrt(3)
    a = 0.25
    expected: dict[str, list[complex]] = {
        "bell_phi_plus": [s2, 0, 0, s2],
        "bell_phi_minus": [s2, 0, 0, -s2],
        "bell_psi_plus": [0, s2, s2, 0],
        "bell_psi_minus": [0, s2, -s2, 0],
        "ghz3": [s2, 0, 0, 0, 0, 0, 0, s2],
        "w3": [0, s3, s3, 0, s3, 0, 0, 0],
        "ghz4": [s2] + [0] * 14 + [s2],
        "w4": [0, 0.5, 0.5, 0, 0.5, 0, 0, 0, 0.5, 0, 0, 0, 0, 0, 0, 0],
        "cluster4_ideal": [a, a, a, -a, a, a, -a, a, a, a, -a, a, a, a, a, -a],
    }
    print("\nBasis-match verification (generated vs existing idealStates.ts):")
    all_pass = True
    for fid, (stype, n, params) in _NAMED_STATEVECTORS.items():
        gen = np.array(
            [complex(re, im) for re, im in _frontend_statevector(stype, n, params)]
        )
        exp = _canonical_global_phase(np.array(expected[fid], dtype=complex))
        diff = float(np.max(np.abs(gen - exp)))
        ok = diff < 1e-9
        all_pass = all_pass and ok
        print(f"  {'PASS' if ok else 'FAIL'}  {fid:16s} max|diff|={diff:.2e}")
    print("ALL PASS" if all_pass else "SOME MISMATCHES (see above)")


if __name__ == "__main__":
    main()
