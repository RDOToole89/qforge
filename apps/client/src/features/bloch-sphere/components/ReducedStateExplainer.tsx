'use dom';

/**
 * Educational panel shown in the right sidebar during experiment mode.
 * Explains what the user is seeing with context-appropriate content.
 */

import { chrome, viz } from "@/src/design/tokens";

interface ReducedStateExplainerProps {
  context: "single" | "multi" | "diagonal_warning" | "multi_qubit_insight";
  purity?: number;
  numQubits?: number;
  sourceMode?: string;
}

const cS: React.CSSProperties = {
  background: `${viz.cyan}0f`,
  border: `1px solid ${viz.cyan}26`,
  borderRadius: "8px",
  padding: "10px 12px",
  fontSize: "11.5px",
  lineHeight: "1.55",
  color: chrome.text.secondary,
};

const cT: React.CSSProperties = {
  color: viz.cyan,
  fontWeight: 600,
  fontSize: "10px",
  letterSpacing: "0.5px",
  marginBottom: "5px",
};

export default function ReducedStateExplainer({
  context,
  purity,
  numQubits,
  sourceMode,
}: ReducedStateExplainerProps) {
  if (context === "single") {
    return (
      <div style={cS}>
        <div style={cT}>REDUCED DENSITY MATRIX</div>
        <span style={{ color: chrome.text.secondary }}>
          When {numQubits ?? "N"} qubits are entangled, tracing out{" "}
          {numQubits ? numQubits - 1 : "N−1"} gives the <em>local</em> state of one qubit.
          A pure global state can yield a mixed local state.
        </span>
        {purity !== undefined && (
          <div style={{ marginTop: "6px", fontSize: "10.5px" }}>
            <span style={{ color: viz.cyan, fontWeight: 600 }}>Purity = {purity.toFixed(3)}</span>
            {" — "}
            {purity > 0.95
              ? "nearly pure, this qubit retains coherence"
              : purity > 0.6
                ? "partially mixed, some decoherence or entanglement"
                : "significantly mixed (0.5 = maximally mixed for a qubit)"}
          </div>
        )}
      </div>
    );
  }

  if (context === "diagonal_warning") {
    return (
      <div style={{
        ...cS,
        background: `${chrome.status.warning}0f`,
        border: `1px solid ${chrome.status.warning}26`,
      }}>
        <div style={{ ...cT, color: chrome.status.warning }}>Z-BASIS ONLY</div>
        <span style={{ color: chrome.text.secondary }}>
          Only Z-basis measurements were available. The Bloch vector's X and Y
          components are zero — this doesn't mean the state has no coherence,
          just that we can't see it from computational basis measurements alone.
        </span>
        <div style={{ marginTop: "6px", fontSize: "10.5px", color: chrome.text.secondary }}>
          Re-run in <code style={{ color: chrome.status.warning }}>density_matrix</code> mode
          for the full picture.
        </div>
      </div>
    );
  }

  if (context === "multi_qubit_insight") {
    return (
      <div style={cS}>
        <div style={cT}>STRUCTURED DECOHERENCE</div>
        <span style={{ color: chrome.text.secondary }}>
          Non-uniform Bloch vector lengths across qubits indicate structured
          decoherence — some qubits decohere faster than others based on their
          position in the entanglement network.
        </span>
        {sourceMode === "diagonal_estimate" && (
          <div style={{ marginTop: "6px", fontSize: "10.5px", color: chrome.text.secondary }}>
            Note: diagonal estimate only shows Z-component variation.
          </div>
        )}
      </div>
    );
  }

  // context === "multi" (2-qubit tab)
  return (
    <div style={cS}>
      <div style={cT}>TWO-QUBIT CORRELATORS</div>
      <span style={{ color: chrome.text.secondary }}>
        These are actual expectation values from the experiment's density matrix.
        Unlike the built-in mode (which simulates noise), these values reflect
        the real quantum state after preparation and noise.
      </span>
    </div>
  );
}
