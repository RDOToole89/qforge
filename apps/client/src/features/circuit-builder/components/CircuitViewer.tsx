import { useState, useCallback } from "react";
import CircuitCanvas from "./CircuitCanvas";
import { getGateDef } from "../data/gateLibrary";
import { colors, fonts } from "../styles";
import type { Circuit, PlacedGate } from "../types";

interface CircuitViewerProps {
  circuit: Circuit;
}

/** Read-only circuit visualization with educational gate tooltips. */
export function CircuitViewer({ circuit }: CircuitViewerProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const selectedGate = selectedId
    ? circuit.moments
        .flatMap((m) => m.gates)
        .find((g) => g.id === selectedId) ?? null
    : null;

  const handleGateClick = useCallback((gateId: string) => {
    setSelectedId((prev) => (prev === gateId ? null : gateId));
  }, []);

  const handleCanvasClick = useCallback(() => {
    setSelectedId(null);
  }, []);

  return (
    <div>
      <CircuitCanvas
        circuit={circuit}
        selectedGateId={selectedId}
        onGateClick={handleGateClick}
        onCanvasClick={handleCanvasClick}
      />
      {selectedGate && <GateTooltip gate={selectedGate} />}
    </div>
  );
}

function GateTooltip({ gate }: { gate: PlacedGate }) {
  const def = getGateDef(gate.gateType);
  const qubitLabel =
    gate.qubits.length === 1
      ? `q[${gate.qubits[0]}]`
      : gate.qubits.map((q) => `q[${q}]`).join(", ");

  const paramLabel =
    def.parametric && gate.params?.[0] !== undefined
      ? `${(gate.params[0] / Math.PI).toFixed(3)}\u03c0 rad`
      : null;

  return (
    <div
      style={{
        marginTop: 8,
        padding: "10px 14px",
        background: colors.card,
        border: `1px solid ${def.color}40`,
        borderLeft: `3px solid ${def.color}`,
        borderRadius: 8,
        fontSize: 12,
        fontFamily: fonts.sans,
        lineHeight: 1.6,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            width: 28,
            height: 28,
            borderRadius: 6,
            background: `${def.color}20`,
            border: `1px solid ${def.color}40`,
            color: def.color,
            fontFamily: fonts.mono,
            fontWeight: 700,
            fontSize: 13,
          }}
        >
          {def.label}
        </span>
        <span style={{ color: colors.text, fontWeight: 600, fontSize: 13 }}>
          {def.name}
        </span>
        <span style={{ color: colors.textTertiary, fontSize: 11, marginLeft: "auto" }}>
          {qubitLabel}
        </span>
      </div>
      <div style={{ color: colors.textSecondary, fontSize: 11.5 }}>
        {def.description}
      </div>
      {paramLabel && (
        <div style={{ color: colors.textTertiary, fontSize: 11, marginTop: 4, fontFamily: fonts.mono }}>
          Angle: {paramLabel}
        </div>
      )}
    </div>
  );
}
