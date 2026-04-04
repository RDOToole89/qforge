import { colors, fonts } from "../styles";
import { SINGLE_QUBIT_GATES, MULTI_QUBIT_GATES, getGateDef } from "../data/gateLibrary";
import type { GateType } from "../types";

interface GatePaletteProps {
  onGateSelect: (gateType: GateType) => void;
  activeGate: GateType | null;
  numQubits: number;
}

export default function GatePalette({ onGateSelect, activeGate, numQubits }: GatePaletteProps) {
  return (
    <div style={{
      display: "flex",
      gap: 6,
      padding: "8px 12px",
      background: colors.surface,
      borderRadius: 8,
      border: `1px solid ${colors.border}`,
      flexWrap: "wrap",
      alignItems: "center",
    }}>
      {/* Single-qubit gates */}
      {SINGLE_QUBIT_GATES.map((gt) => {
        const def = getGateDef(gt);
        const isActive = activeGate === gt;
        return (
          <button
            key={gt}
            onClick={() => onGateSelect(gt)}
            title={def.name}
            style={{
              width: 38,
              height: 38,
              borderRadius: 6,
              border: `1.5px solid ${isActive ? colors.accentLight : def.color}`,
              background: isActive ? colors.accentDim : colors.card,
              color: isActive ? colors.accentLight : def.color,
              fontFamily: fonts.mono,
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
              transition: "all 0.15s ease",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {def.label}
          </button>
        );
      })}

      {/* Separator */}
      <div style={{
        width: 1,
        height: 28,
        background: colors.border,
        margin: "0 4px",
      }} />

      {/* Multi-qubit gates */}
      {MULTI_QUBIT_GATES.map((gt) => {
        const def = getGateDef(gt);
        const isActive = activeGate === gt;
        const disabled = numQubits < def.numQubits;
        return (
          <button
            key={gt}
            onClick={() => !disabled && onGateSelect(gt)}
            title={disabled ? `Needs ${def.numQubits}+ qubits` : def.name}
            disabled={disabled}
            style={{
              width: 38,
              height: 38,
              borderRadius: 6,
              border: `1.5px solid ${disabled ? colors.border : isActive ? colors.accentLight : def.color}`,
              background: isActive ? colors.accentDim : colors.card,
              color: disabled ? colors.textTertiary : isActive ? colors.accentLight : def.color,
              fontFamily: fonts.mono,
              fontSize: 11,
              fontWeight: 600,
              cursor: disabled ? "not-allowed" : "pointer",
              opacity: disabled ? 0.5 : 1,
              transition: "all 0.15s ease",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {def.label}
          </button>
        );
      })}
    </div>
  );
}
