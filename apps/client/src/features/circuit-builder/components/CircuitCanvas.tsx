import { useRef, useCallback, useState } from "react";
import { colors, layout, fonts, momentX, wireY, canvasWidth, canvasHeight } from "../styles";
import GateBlock from "./GateBlock";
import type { Circuit } from "../types";

interface CircuitCanvasProps {
  circuit: Circuit;
  selectedGateId: string | null;
  onGateClick: (gateId: string) => void;
  onGateDoubleClick?: (gateId: string) => void;
  onCanvasClick: (qubit: number) => void;
  /** Called when a gate is dropped from the palette onto a qubit wire */
  onDrop?: (gateType: string, qubit: number) => void;
  /** Show moment column grid lines */
  showGrid?: boolean;
  /** Highlight column/wire during drag */
  dropTarget?: { momentIndex: number; qubit: number } | null;
}

export default function CircuitCanvas({
  circuit,
  selectedGateId,
  onGateClick,
  onCanvasClick,
  onGateDoubleClick,
  onDrop,
  showGrid = false,
  dropTarget,
}: CircuitCanvasProps) {
  const { numQubits, moments } = circuit;
  const svgRef = useRef<SVGSVGElement>(null);
  const [dragQubit, setDragQubit] = useState<number | null>(null);

  // Compute dimensions -- ensure minimum width fills the container
  const contentWidth = canvasWidth(moments.length);
  const height = canvasHeight(numQubits);

  // Determine which qubit wire was clicked from the Y coordinate
  const handleSvgClick = useCallback(
    (e: React.MouseEvent<SVGSVGElement>) => {
      const svg = svgRef.current;
      if (!svg) return;
      const rect = svg.getBoundingClientRect();
      const clickY = e.clientY - rect.top;
      // Find the closest qubit wire
      let closest = 0;
      let closestDist = Infinity;
      for (let i = 0; i < numQubits; i++) {
        const wy = wireY(i);
        const dist = Math.abs(clickY - wy);
        if (dist < closestDist) {
          closestDist = dist;
          closest = i;
        }
      }
      onCanvasClick(closest);
    },
    [numQubits, onCanvasClick],
  );

  // Helper: find closest qubit wire from a mouse event
  const closestQubit = useCallback(
    (e: React.DragEvent | React.MouseEvent) => {
      const svg = svgRef.current;
      if (!svg) return 0;
      const rect = svg.getBoundingClientRect();
      const y = e.clientY - rect.top;
      let best = 0;
      let bestDist = Infinity;
      for (let i = 0; i < numQubits; i++) {
        const d = Math.abs(y - wireY(i));
        if (d < bestDist) { bestDist = d; best = i; }
      }
      return best;
    },
    [numQubits],
  );

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = "copy";
      setDragQubit(closestQubit(e));
    },
    [closestQubit],
  );

  const handleDragLeave = useCallback(() => setDragQubit(null), []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragQubit(null);
      const gateType = e.dataTransfer.getData("gate-type");
      if (gateType && onDrop) {
        onDrop(gateType, closestQubit(e));
      }
    },
    [closestQubit, onDrop],
  );

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      style={{
        width: "100%",
        overflowX: "auto",
        overflowY: "hidden",
        borderRadius: 8,
        border: `1px solid ${dragQubit !== null ? colors.accent : colors.border}`,
        background: colors.surface,
        transition: "border-color 0.15s ease",
      }}
    >
      <svg
        ref={svgRef}
        width="100%"
        height={height}
        viewBox={`0 0 ${Math.max(contentWidth, 800)} ${height}`}
        preserveAspectRatio="xMinYMid meet"
        onClick={handleSvgClick}
        style={{ display: "block", minWidth: contentWidth }}
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
              q[{i}]
            </text>
          );
        })}

        {/* Qubit wires -- span full viewBox width */}
        {Array.from({ length: numQubits }, (_, i) => {
          const y = wireY(i);
          return (
            <line
              key={`wire-${i}`}
              x1={layout.labelWidth + layout.padding}
              y1={y}
              x2={Math.max(contentWidth, 800) - layout.padding}
              y2={y}
              stroke={colors.wire}
              strokeWidth={1.5}
            />
          );
        })}

        {/* Drag target highlight */}
        {dragQubit !== null && (
          <rect
            x={layout.labelWidth + layout.padding - 4}
            y={wireY(dragQubit) - layout.wireSpacing / 2 + 4}
            width={Math.max(contentWidth, 800) - layout.labelWidth - layout.padding * 2 + 8}
            height={layout.wireSpacing - 8}
            rx={6}
            fill={colors.dropZone}
            stroke={colors.dropZoneBorder}
            strokeWidth={1}
            strokeDasharray="6 3"
          />
        )}

        {/* Moment grid -- full column backgrounds with index labels */}
        {showGrid &&
          Array.from({ length: Math.max(moments.length + 2, 8) }, (_, mi) => {
            const x = momentX(mi);
            const colLeft = x - layout.momentWidth / 2;
            return (
              <g key={`grid-${mi}`}>
                {/* Column background (alternating) */}
                <rect
                  x={colLeft}
                  y={layout.padding}
                  width={layout.momentWidth}
                  height={height - layout.padding * 2}
                  fill={mi % 2 === 0 ? "rgba(99, 102, 241, 0.04)" : "transparent"}
                  stroke={colors.border}
                  strokeWidth={0.5}
                  opacity={0.5}
                />
                {/* Moment index label at top */}
                <text
                  x={x}
                  y={layout.padding + 10}
                  textAnchor="middle"
                  fill={colors.textTertiary}
                  fontSize={9}
                  fontFamily={fonts.mono}
                  opacity={0.6}
                >
                  {mi}
                </text>
              </g>
            );
          })}

        {/* Moment column guides (when grid is off, show subtle dashes) */}
        {!showGrid &&
          moments.map((_, mi) => {
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
              onDoubleClick={onGateDoubleClick}
            />
          )),
        )}

        {/* Empty state indicator */}
        {moments.length === 0 && (
          <text
            x={Math.max(contentWidth, 800) / 2}
            y={height / 2}
            textAnchor="middle"
            dominantBaseline="central"
            fill={colors.textTertiary}
            fontSize={14}
            fontFamily={fonts.sans}
          >
            Click on a gate above, then click a qubit wire to place it
          </text>
        )}
      </svg>
    </div>
  );
}
