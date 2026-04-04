import { colors, fonts } from "../styles";

interface CircuitToolbarProps {
  numQubits: number;
  onSetNumQubits: (n: number) => void;
  onClear: () => void;
  onRun?: () => void;
  isRunning?: boolean;
}

export default function CircuitToolbar({
  numQubits,
  onSetNumQubits,
  onClear,
  onRun,
  isRunning,
}: CircuitToolbarProps) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "10px 12px",
        background: colors.surface,
        borderRadius: 8,
        border: `1px solid ${colors.border}`,
        flexWrap: "wrap",
      }}
    >
      {/* Title */}
      <span
        style={{
          color: colors.text,
          fontSize: 16,
          fontWeight: 700,
          fontFamily: fonts.sans,
          marginRight: 8,
        }}
      >
        Circuit Builder
      </span>

      {/* Qubit count selector */}
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <label
          style={{
            color: colors.textSecondary,
            fontSize: 12,
            fontFamily: fonts.sans,
          }}
        >
          Qubits
        </label>
        <select
          value={numQubits}
          onChange={(e) => onSetNumQubits(Number(e.target.value))}
          style={{
            background: colors.card,
            color: colors.text,
            border: `1px solid ${colors.border}`,
            borderRadius: 6,
            padding: "4px 8px",
            fontSize: 13,
            fontFamily: fonts.mono,
            cursor: "pointer",
          }}
        >
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </div>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Clear button */}
      <button
        onClick={onClear}
        style={{
          background: "transparent",
          color: colors.textSecondary,
          border: `1px solid ${colors.border}`,
          borderRadius: 6,
          padding: "6px 14px",
          fontSize: 12,
          fontFamily: fonts.sans,
          fontWeight: 500,
          cursor: "pointer",
          transition: "all 0.15s",
        }}
      >
        Clear
      </button>

      {/* Run button */}
      {onRun && (
        <button
          onClick={onRun}
          disabled={isRunning}
          style={{
            background: isRunning ? colors.border : colors.accent,
            color: isRunning ? colors.textTertiary : "#fff",
            border: "none",
            borderRadius: 6,
            padding: "6px 18px",
            fontSize: 13,
            fontFamily: fonts.sans,
            fontWeight: 600,
            cursor: isRunning ? "wait" : "pointer",
            transition: "all 0.15s",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          {isRunning ? "Running..." : "\u25B6 Run"}
        </button>
      )}
    </div>
  );
}
