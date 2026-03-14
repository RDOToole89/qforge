'use dom';

/**
 * Educational panel shown in the right sidebar during experiment mode.
 * Explains what the user is seeing with context-appropriate content.
 */

interface ReducedStateExplainerProps {
  context: "single" | "multi" | "diagonal_warning" | "multi_qubit_insight";
  purity?: number;
  numQubits?: number;
  sourceMode?: string;
}

const cS: React.CSSProperties = {
  background: "rgba(68,200,255,0.06)",
  border: "1px solid rgba(68,200,255,0.15)",
  borderRadius: "8px",
  padding: "10px 12px",
  fontSize: "11.5px",
  lineHeight: "1.55",
  color: "#7a8ea8",
};

const cT: React.CSSProperties = {
  color: "#44c8ff",
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
        <span style={{ color: "#a0b0c0" }}>
          When {numQubits ?? "N"} qubits are entangled, tracing out{" "}
          {numQubits ? numQubits - 1 : "N\u22121"} gives the <em>local</em> state of one qubit.
          A pure global state can yield a mixed local state.
        </span>
        {purity !== undefined && (
          <div style={{ marginTop: "6px", fontSize: "10.5px" }}>
            <span style={{ color: "#44c8ff", fontWeight: 600 }}>Purity = {purity.toFixed(3)}</span>
            {" \u2014 "}
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
        background: "rgba(255,200,50,0.06)",
        border: "1px solid rgba(255,200,50,0.15)",
      }}>
        <div style={{ ...cT, color: "#dda030" }}>Z-BASIS ONLY</div>
        <span style={{ color: "#b0a080" }}>
          Only Z-basis measurements were available. The Bloch vector's X and Y
          components are zero — this doesn't mean the state has no coherence,
          just that we can't see it from computational basis measurements alone.
        </span>
        <div style={{ marginTop: "6px", fontSize: "10.5px", color: "#a09070" }}>
          Re-run in <code style={{ color: "#dda030" }}>density_matrix</code> mode
          for the full picture.
        </div>
      </div>
    );
  }

  if (context === "multi_qubit_insight") {
    return (
      <div style={cS}>
        <div style={cT}>STRUCTURED DECOHERENCE</div>
        <span style={{ color: "#a0b0c0" }}>
          Non-uniform Bloch vector lengths across qubits indicate structured
          decoherence — some qubits decohere faster than others based on their
          position in the entanglement network.
        </span>
        {sourceMode === "diagonal_estimate" && (
          <div style={{ marginTop: "6px", fontSize: "10.5px", color: "#a09070" }}>
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
      <span style={{ color: "#a0b0c0" }}>
        These are actual expectation values from the experiment's density matrix.
        Unlike the built-in mode (which simulates noise), these values reflect
        the real quantum state after preparation and noise.
      </span>
    </div>
  );
}
