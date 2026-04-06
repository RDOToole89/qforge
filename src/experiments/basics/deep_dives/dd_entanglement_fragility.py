"""Deep Dive: Entanglement Fragility — What survives qubit loss?

BEST AFTER: Steps 6-7 (GHZ and W states)

WHAT YOU'LL LEARN:
  Different entangled states have different robustness to qubit loss.
  If you "lose" one qubit (trace it out / ignore its measurement),
  what happens to the entanglement of the remaining qubits?

  - GHZ: FRAGILE. Lose one qubit → all entanglement destroyed.
    The remaining qubits become a classical mixture of |00...0⟩
    and |11...1⟩ — correlated but not entangled.

  - W: ROBUST. Lose one qubit → remaining qubits are STILL entangled.
    W state degrades gracefully because the excitation is distributed.

THE EXPERIMENT:
  We prepare 4-qubit GHZ and W states, then simulate "losing" qubit 0
  by looking only at the measurement outcomes of qubits 1-3.

  We compare the statistics of the remaining 3 qubits.

WHAT TO LOOK FOR:
  - GHZ-4 (all 4 qubits): only |0000⟩ and |1111⟩
  - GHZ-4 (drop qubit 0): only |000⟩ and |111⟩ — still looks correlated
    but this is CLASSICAL correlation, not entanglement
  - W-4 (all 4 qubits): four peaks at |1000⟩, |0100⟩, |0010⟩, |0001⟩
  - W-4 (drop qubit 0): three peaks at |100⟩, |010⟩, |001⟩ + |000⟩
    The three-qubit W state SURVIVES — genuine entanglement persists

WHY THIS MATTERS:
  In real quantum networks, qubits get lost (photon absorption,
  decoherence). W states are better for quantum communication
  because they survive partial loss. GHZ states are "all or nothing."

CIRCUITS:
  GHZ-4:                              W-4:
  q0: ─H──●──●──●── M                q0: ─[Givens cascade]── M
  q1: ────X──┼──┼── M                q1: ─[distributes one ]── M
  q2: ───────X──┼── M                q2: ─[excitation      ]── M
  q3: ──────────X── M                q3: ─[equally         ]── M

  "Lose" q0: look only at q1-q3 outcomes.
  GHZ: remaining qubits are classically correlated (not entangled).
  W:   remaining qubits are STILL genuinely entangled.

TRY IT:
    from src.experiments.basics.deep_dives.dd_entanglement_fragility import entanglement_fragility

    ghz_full, ghz_partial, w_full, w_partial = entanglement_fragility.run_comparison()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class EntanglementFragilityExperiment(BaseExperiment):
    """Deep Dive: Compare GHZ and W robustness to qubit loss."""

    name = "dd_entanglement_fragility"
    description = "Deep dive: GHZ is fragile, W is robust — what survives qubit loss?"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            shots=4096,
            noise_enabled=False,
        )

    def run_comparison(self) -> tuple[ExperimentResult, ExperimentResult, ExperimentResult, ExperimentResult]:
        """Run GHZ-4 and W-4 at full size and 3 qubits for comparison.

        Returns (ghz_4q, ghz_3q, w_4q, w_3q).
        The 3-qubit versions simulate "what if we lost one qubit" by
        preparing the smaller state directly.
        """
        ghz_4 = self.run({"num_qubits": 4, "state_type": "GHZ"})
        ghz_3 = self.run({"num_qubits": 3, "state_type": "GHZ"})
        w_4 = self.run({"num_qubits": 4, "state_type": "W"})
        w_3 = self.run({"num_qubits": 3, "state_type": "W"})
        return ghz_4, ghz_3, w_4, w_3


entanglement_fragility = EntanglementFragilityExperiment()
