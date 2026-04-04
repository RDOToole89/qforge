import { colors, layout, fonts, momentX, wireY, canvasWidth, canvasHeight } from "../styles";
import GateBlock from "./GateBlock";
import type { Circuit } from "../types";

interface CircuitCanvasProps {
  circuit: Circuit;
  selectedGateId: string | null;
  onGateClick: (gateId: string) => void;
  onCanvasClick: () => void;
  /** Highlight column/wire during drag */
  dropTarget?: { momentIndex: number; qubit: number } | null;
}

export default function CircuitCanvas({
  circuit,
  selectedGateId,
  onGateClick,
  onCanvasClick,
  dropTarget,
}: CircuitCanvasProps) {
  const { numQubits, moments } = circuit;
  const width = canvasWidth(moments.length);
  const height = canvasHeight(numQubits);
  const wireEnd = width - layout.padding;

  return (
    <div
      style={{
        width: "100%",
        overflowX: "auto",
        overflowY: "hidden",
        borderRadius: 8,
        border: `1px solid ${colors.border}`,
        background: colors.surface,
      }}
    >
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        onClick={onCanvasClick}
        style={{ display: "block", minWidth: width }}
      >
        {/* Qubit labels */}
        {Array.from({ length: numQubits }, (_, i) => {
          const y = wireY(i);
          return (
            <text
              key={`label-${i}`}
              x={layout.padding + 8}
              y={y + 1}
              textAnchor="start"
              dominantBaseline="central"
              fill={colors.textSecondary}
              fontSize={13}
              fontFamily={fonts.mono}
            >
              |q{i}\u27E9
            </text>
          );
        })}

        {/* Qubit wires */}
        {Array.from({ length: numQubits }, (_, i) => {
          const y = wireY(i);
          return (
            <line
              key={`wire-${i}`}
              x1={layout.labelWidth + layout.padding}
              y1={y}
              x2={wireEnd}
              y2={y}
              stroke={colors.wire}
              strokeWidth={1.5}
            />
          );
        })}

        {/* Moment column guides (subtle) */}
        {moments.map((_, mi) => {
          const x = momentX(mi);
          return (
            <line
              key={`col-${mi}`}
              x1={x}
              y1={layout.padding + 10}
              x2={x}
              y2={height - layout.padding}
              stroke={colors.border}
              strokeWidth={0.5}
              strokeDasharray="2 4"
              opacity={0.4}
            />
          );
        })}

        {/* Drop zone highlight */}
        {dropTarget && (
          <rect
            x={momentX(dropTarget.momentIndex) - layout.gateSize / 2 - 4}
            y={wireY(dropTarget.qubit) - layout.gateSize / 2 - 4}
            width={layout.gateSize + 8}
            height={layout.gateSize + 8}
            rx={8}
            fill={colors.dropZone}
            stroke={colors.dropZoneBorder}
            strokeWidth={1.5}
            strokeDasharray="4 3"
          />
        )}

        {/* Gate blocks */}
        {moments.map((moment, mi) =>
          moment.gates.map((gate) => (
            <GateBlock
              key={gate.id}
              gate={gate}
              momentIndex={mi}
              selected={gate.id === selectedGateId}
              onClick={onGateClick}
            />
          ))
        )}

        {/* Empty state indicator */}
        {moments.length === 0 && (
          <text
            x={width / 2}
            y={height / 2}
            textAnchor="middle"
            dominantBaseline="central"
            fill={colors.textTertiary}
            fontSize={14}
            fontFamily={fonts.sans}
          >
            Drag a gate from the palette to get started
          </text>
        )}
      </svg>
    </div>
  );
}
