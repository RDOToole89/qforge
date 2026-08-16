import { useRef, useCallback, useState, useEffect } from "react";
import { colors, layout, fonts, momentX, wireY, canvasWidth, canvasHeight, withAlpha } from "../styles";
import GateBlock from "./GateBlock";
import { getGateDef } from "../data/gateLibrary";
import type { Circuit } from "../types";

interface CircuitCanvasProps {
  circuit: Circuit;
  selectedGateId: string | null;
  onGateClick: (gateId: string) => void;
  onGateDoubleClick?: (gateId: string) => void;
  onGateContextMenu?: (gateId: string, event: React.MouseEvent) => void;
  onCanvasClick: (qubit: number, event?: React.MouseEvent) => void;
  /** Called when a gate is dropped from the palette onto a qubit wire */
  onDrop?: (gateType: string, qubit: number, momentIndex: number, event?: React.DragEvent) => void;
  /** Called when a placed gate is repositioned via drag */
  onGateMove?: (gateId: string, qubit: number, momentIndex: number) => void;
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
  onGateContextMenu,
  onGateMove,
  onDrop,
  showGrid = false,
  dropTarget,
}: CircuitCanvasProps) {
  const { numQubits, moments } = circuit;
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dragQubit, setDragQubit] = useState<number | null>(null);
  const [containerWidth, setContainerWidth] = useState(800);


  // Track actual container width so wires extend to the edge
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      setContainerWidth(entry.contentRect.width);
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Compute dimensions -- wires extend to full container width
  const contentWidth = canvasWidth(moments.length);
  const viewBoxWidth = Math.max(contentWidth, containerWidth);
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
      onCanvasClick(closest, e);
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
      // Don't set dropEffect — let the browser match it to effectAllowed automatically
      setDragQubit(closestQubit(e));
    },
    [closestQubit],
  );

  const handleDragLeave = useCallback(() => setDragQubit(null), []);

  // Find closest moment column from a drag event
  const closestMoment = useCallback(
    (e: React.DragEvent) => {
      const svg = svgRef.current;
      if (!svg) return 0;
      const rect = svg.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      let best = 0, bestDist = Infinity;
      const maxM = Math.max(moments.length + 2, 4);
      for (let mi = 0; mi < maxM; mi++) {
        const d = Math.abs(mx - momentX(mi));
        if (d < bestDist) { bestDist = d; best = mi; }
      }
      return best;
    },
    [moments.length],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragQubit(null);
      const moveId = e.dataTransfer.getData("gate-move-id");
      const gateType = e.dataTransfer.getData("gate-type");

      if (moveId && onGateMove) {
        // Moving an existing gate
        const qubit = closestQubit(e);
        const mi = closestMoment(e);
        onGateMove(moveId, qubit, mi);
      } else if (gateType && onDrop) {
        // Placing a new gate from the palette — snap to drop position
        onDrop(gateType, closestQubit(e), closestMoment(e), e);
      }
    },
    [closestQubit, closestMoment, onDrop, onGateMove, onGateClick],
  );

  // Compute gate positions for draggable overlays (in viewBox coords —
  // positioned inside a wrapper that matches SVG dimensions exactly)
  const gateDragOverlays = moments.flatMap((moment, mi) =>
    moment.gates.map((gate) => {
      const gx = momentX(mi);
      const minQ = Math.min(...gate.qubits);
      const maxQ = Math.max(...gate.qubits);
      const gyTop = wireY(minQ);
      const gyBot = wireY(maxQ);
      const pad = 8;
      return {
        left: gx - layout.gateSize / 2 - pad,
        top: gyTop - layout.gateSize / 2 - pad,
        width: layout.gateSize + pad * 2,
        height: (gyBot - gyTop) + layout.gateSize + pad * 2,
        gateType: gate.gateType,
        gateId: gate.id,
      };
    }),
  );

  return (
    <div
      ref={containerRef}
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
        position: "relative",
      }}
    >
      <svg
        ref={svgRef}
        width="100%"
        height={height}
        viewBox={`0 0 ${viewBoxWidth} ${height}`}
        preserveAspectRatio="xMinYMid meet"
        onClick={handleSvgClick}
        style={{
          display: "block",
          minWidth: contentWidth > containerWidth ? contentWidth : undefined,
          userSelect: "none",
          WebkitUserSelect: "none",
        } as React.CSSProperties}
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
              x2={viewBoxWidth - layout.padding}
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
            width={viewBoxWidth - layout.labelWidth - layout.padding * 2 + 8}
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
                  fill={mi % 2 === 0 ? withAlpha(colors.accent, 0.04) : "transparent"}
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
              onContextMenu={onGateContextMenu}
            />
          )),
        )}

        {/* Empty state indicator */}
        {moments.length === 0 && (
          <text
            x={viewBoxWidth / 2}
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

      {/* Overlay layer: same dimensions as SVG, positioned on top, for draggable gate handles */}
      <div style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: viewBoxWidth,
          height,
          pointerEvents: "none",
        }}
      >
        {gateDragOverlays.map(({ left, top, width: w, height: h, gateType, gateId }) => (
          <div
            key={`drag-${gateId}`}
            draggable
            onDragStart={(e) => {
              e.dataTransfer.setData("gate-type", gateType);
              e.dataTransfer.setData("gate-move-id", gateId);
              e.dataTransfer.effectAllowed = "copyMove";
              onGateClick(gateId);
            }}
            onClick={(e) => {
              e.stopPropagation();
              onGateClick(gateId);
            }}
            onContextMenu={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onGateContextMenu?.(gateId, e as unknown as React.MouseEvent);
            }}
            style={{
              position: "absolute",
              left,
              top,
              width: w,
              height: h,
              cursor: "grab",
              pointerEvents: "auto",
            }}
          />
        ))}
      </div>
    </div>
  );
}
