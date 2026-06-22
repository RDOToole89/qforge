import type { GlossaryCategory, GlossaryTerm } from "../types";
import { viz } from "@/src/design/tokens";

export const category: GlossaryCategory = {
  id: "hardware",
  name: "Quantum Hardware",
  icon: "cpu",
  color: viz.gate.teal,
  description: "Physical implementations and device characteristics",
};

export const terms: GlossaryTerm[] = [
  {
    id: "superconducting_qubit",
    name: "Superconducting Qubit",
    formalDefinition:
      "A qubit implemented using superconducting circuits (Josephson junctions) operating at ~15 mK. Types include transmon, fluxonium, and charge qubits. Gate times ~20-50 ns, T₁ ~ 100-500 μs. Used by IBM, Google, and Rigetti.",
    intuitiveExplanation:
      "An artificial atom made from superconducting metal cooled near absolute zero. The two lowest energy levels of the circuit act as |0⟩ and |1⟩. Fast gates but requires extreme cooling. The dominant platform for quantum computing today.",
    relatedTerms: ["transmon", "t1_time", "t2_time", "quantum_gate"],
    categoryId: "hardware",
  },
  {
    id: "transmon",
    name: "Transmon",
    formalDefinition:
      "A charge-insensitive superconducting qubit: a Cooper pair box operated at large E_J/E_C ratio (typically 50-100). Reduces charge noise sensitivity exponentially at the cost of reduced anharmonicity (~200-300 MHz). The workhorse qubit of IBM Quantum.",
    intuitiveExplanation:
      "The most common superconducting qubit design. By making the circuit less sensitive to stray electric charges, it trades a bit of 'qubit quality' for dramatically better stability. Nearly all IBM and Google quantum processors use transmons.",
    relatedTerms: ["superconducting_qubit", "t1_time", "readout_error"],
    categoryId: "hardware",
  },
  {
    id: "trapped_ion",
    name: "Trapped Ion Qubit",
    formalDefinition:
      "A qubit encoded in the electronic states of a trapped atomic ion (e.g., ⁴⁰Ca⁺, ¹⁷¹Yb⁺). Ions are confined by electromagnetic fields and manipulated with laser pulses. Gate fidelities >99.9%, T₂ up to seconds, but slower gate times (~1-100 μs).",
    intuitiveExplanation:
      "Using actual atoms as qubits — ions floating in an electromagnetic trap, controlled by laser beams. Extremely high quality but slower than superconducting qubits. All qubits are identical (they're atoms!) and any pair can be entangled directly.",
    relatedTerms: ["t1_time", "t2_time", "gate_fidelity"],
    categoryId: "hardware",
  },
  {
    id: "gate_fidelity",
    name: "Gate Fidelity",
    formalDefinition:
      "The fidelity between the ideal unitary operation U and the actual quantum channel E: F = Tr(U†E(ρ))/d averaged over input states. Typically reported as average gate fidelity. State-of-the-art: single-qubit >99.9%, two-qubit >99.5%.",
    intuitiveExplanation:
      "How closely a real quantum gate matches the ideal operation. 99.9% fidelity means the gate introduces ~0.1% error each time. Since algorithms require thousands of gates, even small infidelities compound — driving the need for error correction.",
    keyEquation:
      "F_{\\text{avg}} = \\frac{\\text{Tr}(U^\\dagger \\varepsilon(\\rho))}{d} \\quad \\text{averaged over } \\rho",
    formulaExplanation:
      "Average gate fidelity compares the ideal unitary U with the actual noisy channel ε, averaged over all input states. F = 1 means perfect implementation; F = 0.999 means 0.1% error per gate. Since algorithms chain thousands of gates, even tiny infidelities compound.",
    relatedTerms: ["quantum_gate", "cptp_map", "surface_code"],
    categoryId: "hardware",
  },
  {
    id: "readout_error",
    name: "Readout Error",
    formalDefinition:
      "The probability of misidentifying a qubit's state during measurement. Characterized by P(0|1) (measuring 0 when the state is 1) and P(1|0). Typical values: 0.5-3% for superconducting qubits. Can be mitigated by measurement error mitigation techniques.",
    intuitiveExplanation:
      "How often the measurement detector gives the wrong answer. Even if the qubit is in |0⟩, the detector might report '1' some fraction of the time. This is separate from gate errors and can often be partially corrected in post-processing.",
    relatedTerms: ["measurement", "gate_fidelity", "error_mitigation"],
    categoryId: "hardware",
  },
  {
    id: "error_mitigation",
    name: "Error Mitigation",
    formalDefinition:
      "Classical post-processing techniques that reduce the effect of noise without full error correction. Methods include Zero-Noise Extrapolation (ZNE), Probabilistic Error Cancellation (PEC), and measurement error mitigation. Polynomial overhead, no logical qubits required.",
    intuitiveExplanation:
      "Clever tricks to get better answers from noisy quantum computers without full error correction. Like taking multiple noisy photos and combining them to get a clearer image. Works today on current hardware but has limits as circuits get deeper.",
    relatedTerms: ["readout_error", "cptp_map", "surface_code"],
    categoryId: "hardware",
  },
  {
    id: "quantum_volume",
    name: "Quantum Volume",
    formalDefinition:
      "A single-number benchmark for quantum computer capability: QV = 2^m where m is the largest circuit width for which random square circuits can be executed with heavy output probability >2/3. Captures qubit count, connectivity, gate fidelity, and crosstalk.",
    intuitiveExplanation:
      "A holistic score for how powerful a quantum computer is — not just how many qubits it has, but how well they work together. Higher quantum volume means the device can run deeper, wider circuits reliably. Current leaders: QV ~ 2^7 to 2^10.",
    keyEquation:
      "QV = 2^m, \\quad m = \\max\\{n : \\text{heavy output} > 2/3\\}",
    formulaExplanation:
      "Quantum volume 2^m where m is the largest circuit size that passes a statistical test. 'Heavy output' means the circuit produces bitstrings with above-median probability more than 2/3 of the time. Higher QV means the device can run wider, deeper circuits reliably.",
    relatedTerms: ["gate_fidelity", "circuit_depth", "superconducting_qubit"],
    categoryId: "hardware",
  },
];
