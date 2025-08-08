"""
Glossary of common terms used in the Quantum Experiment Framework.

Provides a small, local, searchable knowledge base for quick lookups in the CLI.
"""

from typing import Dict, List, Tuple


GLOSSARY: Dict[str, str] = {
    # States
    "ghz": "Greenberger–Horne–Zeilinger state: (|0...0> + |1...1>)/√2, maximally entangled across all qubits.",
    "w state": "Equal superposition of single-excitation states, e.g., (|001>+|010>+|100>)/√3 for 3 qubits.",
    "bell state": "Two-qubit maximally entangled states (Φ±, Ψ±).",
    "cluster state": "Graph state built via CZ gates on a lattice (1D ring/line, 2D grid).",
    "superposition": "Product state |+>^n with |+>=(|0>+|1>)/√2; non-entangling baseline for dephasing studies.",
    
    # Simulation modes
    "qasm": "Shot-based sampling of measurement outcomes from a noiseless or noisy circuit.",
    "statevector": "Exact quantum state amplitudes for pure states (no measurement sampling).",
    "density matrix": "Mixed-state representation supporting noise channels and partial traces.",
    
    # Noise models
    "depolarizing": "Replaces the state with maximally mixed with probability p; uniform Pauli errors.",
    "phase flip": "Applies Z with probability p; models pure dephasing (loss of phase coherence).",
    "bit flip": "Applies X with probability p; flips computational basis states.",
    "amplitude damping": "Models energy relaxation (T1) from |1>→|0> with environment coupling.",
    "thermal relaxation": "Combined T1/T2 with temperature-dependent thermal population; realistic hardware model.",
    
    # Metrics
    "shannon entropy": "Classical entropy H(p) = −∑ p_i log p_i of measured distribution.",
    "kl divergence": "Relative entropy D_KL(p||q): how distribution p diverges from reference q.",
    "fubini-study distance": "Distance between pure states from their inner product (projective Hilbert space).",
    "mutual information": "I(A;B) between qubits/subsystems, capturing shared information.",
    "purity": "Tr(ρ^2); 1 for pure states, <1 for mixed states.",
    "von neumann entropy": "S(ρ) = −Tr(ρ log ρ); generalizes Shannon entropy to quantum states.",
    "linear entropy": "1 − Tr(ρ^2); simple impurity measure.",
    "participation ratio": "1/∑ p_i^2; effective number of significantly populated outcomes.",
    "total variation distance": "0.5 ∑|p_i − q_i|; distribution distance used in comparison tests.",
    
    # Visualization
    "histogram": "Bar chart of measurement counts/probabilities across bitstrings.",
    "hypergraph": "Nodes as qubits; hyperedges for multi-qubit correlations above threshold.",
    "bloch sphere": "Geometric representation of single-qubit states; decoherence shrinks vectors to origin.",
}


def list_terms() -> List[Tuple[str, str]]:
    return sorted(GLOSSARY.items(), key=lambda kv: kv[0])


def search_terms(query: str) -> List[Tuple[str, str]]:
    q = query.strip().lower()
    if not q:
        return list_terms()
    results: List[Tuple[str, str]] = []
    for term, desc in GLOSSARY.items():
        if q in term.lower() or q in desc.lower():
            results.append((term, desc))
    return sorted(results, key=lambda kv: kv[0])

