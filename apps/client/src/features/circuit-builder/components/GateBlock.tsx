import { colors, layout, fonts, momentX, wireY } from "../styles";
import { getGateDef } from "../data/gateLibrary";
import type { PlacedGate } from "../types";

/** Format a rotation angle as a readable pi fraction. */
function formatAngle(radians: number): string {
  const ratio = radians / Math.PI;
  const fracs: [number, string][] = [
    [1, "\u03c0"], [-1, "-\u03c0"],
    [0.5, "\u03c0/2"], [-0.5, "-\u03c0/2"],
    [0.25, "\u03c0/4"], [-0.25, "-\u03c0/4"],
    [0.125, "\u03c0/8"], [-0.125, "-\u03c0/8"],
    [0.375, "3\u03c0/8"], [-0.375, "-3\u03c0/8"],
    [0.625, "5\u03c0/8"], [-0.625, "-5\u03c0/8"],
    [0.75, "3\u03c0/4"], [-0.75, "-3\u03c0/4"],
    [2, "2\u03c0"], [-2, "-2\u03c0"],
  ];
  for (const [frac, label] of fracs) {
    if (Math.abs(ratio - frac) < 1e-6) return label;
  }
  if (Math.abs(ratio) > 0.01) return `${ratio.toFixed(2)}\u03c0`;
  return radians.toFixed(3);
}

interface GateBlockProps {
  gate: PlacedGate;
  momentIndex: number;
  selected: boolean;
  onClick: (gateId: string) => void;
  onDoubleClick?: (gateId: string) => void;
  onContextMenu?: (gateId: string, event: React.MouseEvent) => void;
}

// Marching ants CSS — injected once
let marchingAntsInjected = false;
function ensureMarchingAnts() {
  if (marchingAntsInjected) return;
  marchingAntsInjected = true;
  const style = document.createElement("style");
  style.textContent = `
    @keyframes marching-ants {
      to { stroke-dashoffset: -12; }
    }
  `;
  document.head.appendChild(style);
}

export default function GateBlock({ gate, momentIndex, selected, onClick, onDoubleClick, onContextMenu }: GateBlockProps) {
  const def = getGateDef(gate.gateType);
  const x = momentX(momentIndex);
  const targetQubit = gate.qubits[gate.qubits.length - 1];
  const y = wireY(targetQubit);
  const half = layout.gateSize / 2;

  if (selected) ensureMarchingAnts();

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick(gate.id);
  };

  const handleDoubleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDoubleClick?.(gate.id);
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onContextMenu?.(gate.id, e);
  };

  // Compute bounding box for the full gate (including multi-qubit connections)
  const isMultiQubit = def.numQubits >= 2 && gate.qubits.length >= 2;
  const minQ = isMultiQubit ? Math.min(...gate.qubits) : targetQubit;
  const maxQ = isMultiQubit ? Math.max(...gate.qubits) : targetQubit;
  const yTop = wireY(minQ);
  const yBot = wireY(maxQ);

  // Bounding box for selection/hit area
  const pad = 6;
  const bbX = x - half - pad;
  const bbY = yTop - half - pad;
  const bbW = layout.gateSize + pad * 2;
  const bbH = (yBot - yTop) + layout.gateSize + pad * 2;

  // Scale transform for selected state
  const selTransform = selected
    ? `translate(${x}, ${(yTop + yBot) / 2}) scale(1.08) translate(${-x}, ${-(yTop + yBot) / 2})`
    : undefined;

  // Multi-qubit gate rendering
  if (isMultiQubit) {
    const controlQubits = gate.qubits.slice(0, -1);

    return (
      <g
        onClick={handleClick}
        onDoubleClick={handleDoubleClick}
        onContextMenu={handleContextMenu}
        style={{ cursor: "pointer" }}
        transform={selTransform}
      >
        {/* Invisible hit area covering the full gate */}
        <rect
          x={bbX} y={bbY} width={bbW} height={bbH}
          fill="transparent"
          stroke="none"
        />

        {/* Selection: marching ants outline over the full gate */}
        {selected && (
          <>
            {/* Glow background */}
            <rect
              x={bbX} y={bbY} width={bbW} height={bbH}
              rx={10}
              fill={`${colors.accent}08`}
            />
            {/* Marching ants border */}
            <rect
              x={bbX} y={bbY} width={bbW} height={bbH}
              rx={10}
              fill="none"
              stroke={colors.accentLight}
              strokeWidth={1.5}
              strokeDasharray="6 6"
              style={{ animation: "marching-ants 0.4s linear infinite" }}
            />
          </>
        )}

        {/* Vertical connection line */}
        <line
          x1={x} y1={yTop} x2={x} y2={yBot}
          stroke={selected ? colors.accentLight : def.color}
          strokeWidth={2}
        />

        {/* Control dots */}
        {controlQubits.map((cq, i) => (
          <circle
            key={`ctrl-${i}`}
            cx={x} cy={wireY(cq)}
            r={layout.controlDotRadius}
            fill={selected ? colors.accentLight : def.color}
          />
        ))}

        {/* Target rendering */}
        {gate.gateType === "CNOT" ? (
          <g>
            <circle cx={x} cy={y} r={layout.targetRadius} fill="none"
              stroke={selected ? colors.accentLight : def.color} strokeWidth={2} />
            <line x1={x - layout.targetRadius} y1={y} x2={x + layout.targetRadius} y2={y}
              stroke={selected ? colors.accentLight : def.color} strokeWidth={2} />
            <line x1={x} y1={y - layout.targetRadius} x2={x} y2={y + layout.targetRadius}
              stroke={selected ? colors.accentLight : def.color} strokeWidth={2} />
          </g>
        ) : gate.gateType === "CZ" ? (
          <circle cx={x} cy={y} r={layout.controlDotRadius}
            fill={selected ? colors.accentLight : def.color} />
        ) : gate.gateType === "SWAP" ? (
          <>
            {gate.qubits.map((q, i) => {
              const sy = wireY(q);
              const r = 8;
              return (
                <g key={`swap-${i}`}>
                  <line x1={x - r} y1={sy - r} x2={x + r} y2={sy + r}
                    stroke={selected ? colors.accentLight : def.color} strokeWidth={2} />
                  <line x1={x - r} y1={sy + r} x2={x + r} y2={sy - r}
                    stroke={selected ? colors.accentLight : def.color} strokeWidth={2} />
                </g>
              );
            })}
          </>
        ) : (
          <g>
            <rect x={x - half} y={y - half} width={layout.gateSize} height={layout.gateSize}
              rx={6} fill={selected ? colors.accentDim : colors.card}
              stroke={selected ? colors.accentLight : def.color} strokeWidth={selected ? 2 : 1.5} />
            <text x={x} y={y + 1} textAnchor="middle" dominantBaseline="central"
              fill={selected ? colors.accentLight : def.color} fontSize={12}
              fontFamily={fonts.mono} fontWeight={600}>
              {def.label}
            </text>
          </g>
        )}
      </g>
    );
  }

  // Single-qubit gate
  const paramText = def.parametric && gate.params?.[0] !== undefined
    ? `(${formatAngle(gate.params[0])})`
    : "";

  return (
    <g
      onClick={handleClick}
      onContextMenu={handleContextMenu}
      style={{ cursor: "pointer" }}
      transform={selTransform}
    >
      {/* Invisible hit area */}
      <rect
        x={x - half - pad} y={y - half - pad}
        width={layout.gateSize + pad * 2} height={layout.gateSize + pad * 2}
        fill="transparent" stroke="none"
      />

      {/* Selection: marching ants */}
      {selected && (
        <>
          <rect
            x={x - half - pad} y={y - half - pad}
            width={layout.gateSize + pad * 2} height={layout.gateSize + pad * 2}
            rx={10} fill={`${colors.accent}08`}
          />
          <rect
            x={x - half - pad} y={y - half - pad}
            width={layout.gateSize + pad * 2} height={layout.gateSize + pad * 2}
            rx={10} fill="none"
            stroke={colors.accentLight} strokeWidth={1.5} strokeDasharray="6 6"
            style={{ animation: "marching-ants 0.4s linear infinite" }}
          />
        </>
      )}

      {/* Gate box */}
      <rect
        x={x - half} y={y - half}
        width={layout.gateSize} height={layout.gateSize}
        rx={6}
        fill={selected ? colors.accentDim : colors.card}
        stroke={selected ? colors.accentLight : def.color}
        strokeWidth={selected ? 2 : 1.5}
      />
      <text
        x={x} y={paramText ? y - 3 : y + 1}
        textAnchor="middle" dominantBaseline="central"
        fill={selected ? colors.accentLight : def.color}
        fontSize={14} fontFamily={fonts.mono} fontWeight={600}
      >
        {def.label}
      </text>
      {paramText && (
        <text
          x={x} y={y + 12}
          textAnchor="middle" dominantBaseline="central"
          fill={colors.textTertiary} fontSize={9} fontFamily={fonts.mono}
        >
          {paramText}
        </text>
      )}
    </g>
  );
}
