import { colors, layout, fonts, momentX, wireY } from "../styles";
import { getGateDef } from "../data/gateLibrary";
import type { PlacedGate } from "../types";

interface GateBlockProps {
  gate: PlacedGate;
  momentIndex: number;
  selected: boolean;
  onClick: (gateId: string) => void;
}

/** Renders a single gate on the SVG circuit canvas */
export default function GateBlock({ gate, momentIndex, selected, onClick }: GateBlockProps) {
  const def = getGateDef(gate.gateType);
  const x = momentX(momentIndex);
  const targetQubit = gate.qubits[gate.qubits.length - 1];
  const y = wireY(targetQubit);
  const half = layout.gateSize / 2;

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick(gate.id);
  };

  // Multi-qubit gate: draw connection line + control dots
  if (def.numQubits >= 2 && gate.qubits.length >= 2) {
    const controlQubits = gate.qubits.slice(0, -1);
    const minQ = Math.min(...gate.qubits);
    const maxQ = Math.max(...gate.qubits);
    const yTop = wireY(minQ);
    const yBot = wireY(maxQ);

    return (
      <g onClick={handleClick} style={{ cursor: "pointer" }}>
        {/* Vertical connection line */}
        <line
          x1={x}
          y1={yTop}
          x2={x}
          y2={yBot}
          stroke={selected ? colors.accentLight : def.color}
          strokeWidth={2}
        />

        {/* Control dots */}
        {controlQubits.map((cq, i) => (
          <circle
            key={`ctrl-${i}`}
            cx={x}
            cy={wireY(cq)}
            r={layout.controlDotRadius}
            fill={selected ? colors.accentLight : def.color}
          />
        ))}

        {/* Target gate block */}
        {gate.gateType === "CNOT" ? (
          // CNOT target: circle with cross
          <g>
            <circle
              cx={x}
              cy={y}
              r={layout.targetRadius}
              fill="none"
              stroke={selected ? colors.accentLight : def.color}
              strokeWidth={2}
            />
            <line
              x1={x - layout.targetRadius}
              y1={y}
              x2={x + layout.targetRadius}
              y2={y}
              stroke={selected ? colors.accentLight : def.color}
              strokeWidth={2}
            />
            <line
              x1={x}
              y1={y - layout.targetRadius}
              x2={x}
              y2={y + layout.targetRadius}
              stroke={selected ? colors.accentLight : def.color}
              strokeWidth={2}
            />
          </g>
        ) : gate.gateType === "CZ" ? (
          // CZ: two control dots (symmetric)
          <circle
            cx={x}
            cy={y}
            r={layout.controlDotRadius}
            fill={selected ? colors.accentLight : def.color}
          />
        ) : gate.gateType === "SWAP" ? (
          // SWAP: two X marks
          <>
            {gate.qubits.map((q, i) => {
              const sy = wireY(q);
              const r = 8;
              return (
                <g key={`swap-${i}`}>
                  <line x1={x - r} y1={sy - r} x2={x + r} y2={sy + r} stroke={selected ? colors.accentLight : def.color} strokeWidth={2} />
                  <line x1={x - r} y1={sy + r} x2={x + r} y2={sy - r} stroke={selected ? colors.accentLight : def.color} strokeWidth={2} />
                </g>
              );
            })}
          </>
        ) : (
          // Generic multi-qubit: labeled box on target
          <g>
            <rect
              x={x - half}
              y={y - half}
              width={layout.gateSize}
              height={layout.gateSize}
              rx={6}
              fill={selected ? colors.accentDim : colors.card}
              stroke={selected ? colors.accentLight : def.color}
              strokeWidth={selected ? 2 : 1.5}
            />
            <text
              x={x}
              y={y + 1}
              textAnchor="middle"
              dominantBaseline="central"
              fill={selected ? colors.accentLight : def.color}
              fontSize={12}
              fontFamily={fonts.mono}
              fontWeight={600}
            >
              {def.label}
            </text>
          </g>
        )}

        {/* Selection highlight */}
        {selected && (
          <rect
            x={x - half - 4}
            y={yTop - 4}
            width={layout.gateSize + 8}
            height={yBot - yTop + 8}
            rx={8}
            fill="none"
            stroke={colors.accentLight}
            strokeWidth={1}
            strokeDasharray="4 2"
            opacity={0.5}
          />
        )}
      </g>
    );
  }

  // Single-qubit gate: labeled box
  const paramText =
    def.parametric && gate.params?.[0] !== undefined
      ? `(${(gate.params[0] / Math.PI).toFixed(1)}\u03c0)`
      : "";

  return (
    <g onClick={handleClick} style={{ cursor: "pointer" }}>
      <rect
        x={x - half}
        y={y - half}
        width={layout.gateSize}
        height={layout.gateSize}
        rx={6}
        fill={selected ? colors.accentDim : colors.card}
        stroke={selected ? colors.accentLight : def.color}
        strokeWidth={selected ? 2 : 1.5}
      />
      <text
        x={x}
        y={paramText ? y - 3 : y + 1}
        textAnchor="middle"
        dominantBaseline="central"
        fill={selected ? colors.accentLight : def.color}
        fontSize={14}
        fontFamily={fonts.mono}
        fontWeight={600}
      >
        {def.label}
      </text>
      {paramText && (
        <text
          x={x}
          y={y + 12}
          textAnchor="middle"
          dominantBaseline="central"
          fill={colors.textTertiary}
          fontSize={9}
          fontFamily={fonts.mono}
        >
          {paramText}
        </text>
      )}

      {selected && (
        <rect
          x={x - half - 3}
          y={y - half - 3}
          width={layout.gateSize + 6}
          height={layout.gateSize + 6}
          rx={8}
          fill="none"
          stroke={colors.accentLight}
          strokeWidth={1}
          strokeDasharray="4 2"
          opacity={0.5}
        />
      )}
    </g>
  );
}
