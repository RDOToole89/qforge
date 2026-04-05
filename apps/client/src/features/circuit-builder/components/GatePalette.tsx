import { colors, fonts } from "../styles";
import { SINGLE_QUBIT_GATES, MULTI_QUBIT_GATES, getGateDef } from "../data/gateLibrary";
import type { GateType } from "../types";

interface GatePaletteProps {
  onGateSelect: (gateType: GateType) => void;
  activeGate: GateType | null;
  numQubits: number;
}

export default function GatePalette({ onGateSelect, activeGate, numQubits }: GatePaletteProps) {
  const renderGateButton = (gt: GateType, disabled = false) => {
    const def = getGateDef(gt);
    const isActive = activeGate === gt;
    const isMultiQubit = def.numQubits >= 2;

    return (
      <button
        key={gt}
        onClick={() => !disabled && onGateSelect(gt)}
        draggable={!disabled}
        onDragStart={(e) => {
          if (disabled) { e.preventDefault(); return; }
          e.dataTransfer.setData("gate-type", gt);
          e.dataTransfer.effectAllowed = "copyMove";
          onGateSelect(gt);
        }}
        title={disabled ? `Needs ${def.numQubits}+ qubits` : `${def.name} — click or drag to place`}
        disabled={disabled}
        style={{
          width: 38,
          height: 38,
          borderRadius: 6,
          border: `1.5px solid ${disabled ? colors.border : isActive ? colors.accentLight : def.color}`,
          borderBottom: isMultiQubit
            ? `3px solid ${disabled ? colors.border : isActive ? colors.accentLight : def.color}`
            : `1.5px solid ${disabled ? colors.border : isActive ? colors.accentLight : def.color}`,
          background: isActive ? colors.accentDim : colors.card,
          color: disabled ? colors.textTertiary : isActive ? colors.accentLight : def.color,
          fontFamily: fonts.mono,
          fontSize: gt === "Toffoli" || gt === "SWAP" ? 11 : 13,
          fontWeight: 600,
          cursor: disabled ? "not-allowed" : "grab",
          opacity: disabled ? 0.5 : 1,
          transition: "all 0.15s ease",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
        }}
      >
        {def.label}
        {/* Multi-qubit badge */}
        {isMultiQubit && (
          <span style={{
            position: "absolute",
            bottom: -1,
            right: 1,
            fontSize: 7,
            fontWeight: 700,
            fontFamily: fonts.mono,
            color: disabled ? colors.textTertiary : isActive ? colors.accentLight : def.color,
            opacity: 0.7,
            lineHeight: 1,
          }}>
            {def.numQubits}Q
          </span>
        )}
      </button>
    );
  };

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
      {SINGLE_QUBIT_GATES.map((gt) => renderGateButton(gt))}

      {/* Separator */}
      <div style={{
        width: 1,
        height: 28,
        background: colors.border,
        margin: "0 4px",
      }} />

      {MULTI_QUBIT_GATES.map((gt) => {
        const def = getGateDef(gt);
        return renderGateButton(gt, numQubits < def.numQubits);
      })}
    </div>
  );
}
