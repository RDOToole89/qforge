import { useState } from "react";
import { colors, fonts, overlay } from "../styles";
import { SINGLE_QUBIT_GATES, MULTI_QUBIT_GATES, getGateDef } from "../data/gateLibrary";
import type { GateType } from "../types";

/** Convert LaTeX matrix notation to readable plain text */
function formatMatrix(latex: string): string {
  let s = latex;
  // Handle \frac{num}{den} → num/den (must run before brace removal)
  s = s.replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, (_, num, den) => {
    const cleanNum = num.replace(/\\/g, "").replace(/\{|\}/g, "");
    const cleanDen = den.replace(/\\sqrt\{(\d+)\}/g, "\u221A$1").replace(/\\/g, "").replace(/\{|\}/g, "");
    return `${cleanNum}/${cleanDen}`;
  });
  s = s.replace(/\\begin\{pmatrix\}/g, "\n\u2502 ")
    .replace(/\\end\{pmatrix\}/g, " \u2502")
    .replace(/\\\\/g, " \u2502\n\u2502 ")
    .replace(/&/g, "  ")
    .replace(/\\sqrt\{([^}]+)\}/g, "\u221A$1")
    .replace(/\\cos/g, "cos")
    .replace(/\\sin/g, "sin")
    .replace(/\\theta/g, "\u03B8")
    .replace(/\\pi/g, "\u03C0")
    .replace(/\\text\{([^}]+)\}/g, "$1")
    .replace(/\\rangle/g, "\u27E9")
    .replace(/\\langle/g, "\u27E8")
    .replace(/\\otimes/g, "\u2297")
    .replace(/\\cdot/g, "\u00B7")
    .replace(/e\^{([^}]+)}/g, "e^($1)")
    .replace(/-i/g, "\u2212i")
    .replace(/\{|\}/g, "")
    .replace(/\|/g, "|")
    .replace(/ +/g, " ");
  return s.trim();
}

interface GatePaletteProps {
  onGateSelect: (gateType: GateType) => void;
  activeGate: GateType | null;
  numQubits: number;
}

export default function GatePalette({ onGateSelect, activeGate, numQubits }: GatePaletteProps) {
  const [infoPopover, setInfoPopover] = useState<{ gt: GateType; x: number; y: number } | null>(null);

  const renderGateButton = (gt: GateType, disabled = false) => {
    const def = getGateDef(gt);
    const isActive = activeGate === gt;
    const isMultiQubit = def.numQubits >= 2;

    return (
      <button
        key={gt}
        onClick={() => { !disabled && onGateSelect(gt); setInfoPopover(null); }}
        onContextMenu={(e) => {
          e.preventDefault();
          setInfoPopover({ gt, x: e.clientX, y: e.clientY });
        }}
        draggable={!disabled}
        onDragStart={(e) => {
          if (disabled) { e.preventDefault(); return; }
          e.dataTransfer.setData("gate-type", gt);
          e.dataTransfer.effectAllowed = "copyMove";
          onGateSelect(gt);
          setInfoPopover(null);
        }}
        title={disabled ? `Needs ${def.numQubits}+ qubits` : `${def.name} — click or drag to place, right-click for info`}
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
    <>
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

      {/* Gate info popover on right-click */}
      {infoPopover && (() => {
        const def = getGateDef(infoPopover.gt);
        const MARGIN = 16;
        const menuW = 280;
        const menuX = Math.min(infoPopover.x, window.innerWidth - menuW - MARGIN);
        const menuY = Math.max(MARGIN, Math.min(infoPopover.y, window.innerHeight - 250));

        return (
          <>
            <div
              style={{ position: "fixed", inset: 0, zIndex: 8999 }}
              onClick={() => setInfoPopover(null)}
              onContextMenu={(e) => { e.preventDefault(); setInfoPopover(null); }}
            />
            <div style={{
              position: "fixed",
              left: menuX,
              top: menuY,
              width: menuW,
              background: colors.bg,
              border: `1px solid ${colors.border}`,
              borderRadius: 10,
              boxShadow: `0 8px 32px ${overlay(0.5)}`,
              zIndex: 9000,
              overflow: "hidden",
              animation: "fadeIn 0.1s ease",
            }}>
              {/* Header */}
              <div style={{
                padding: "10px 14px",
                borderBottom: `1px solid ${colors.border}`,
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}>
                <span style={{
                  background: `${def.color}20`,
                  color: def.color,
                  padding: "2px 8px",
                  borderRadius: 4,
                  fontFamily: fonts.mono,
                  fontSize: 12,
                  fontWeight: 700,
                }}>
                  {def.label}
                </span>
                <span style={{ fontSize: 13, fontWeight: 600, color: colors.text, fontFamily: fonts.sans }}>
                  {def.name}
                </span>
                {def.numQubits >= 2 && (
                  <span style={{ fontSize: 9, color: colors.textTertiary, fontFamily: fonts.mono }}>
                    {def.numQubits}Q
                  </span>
                )}
              </div>

              {/* Description */}
              <div style={{
                padding: "10px 14px",
                fontSize: 12,
                color: colors.textSecondary,
                lineHeight: 1.6,
                fontFamily: fonts.sans,
                borderBottom: `1px solid ${colors.border}`,
              }}>
                {def.description}
              </div>

              {/* Matrix — render LaTeX as readable plain text */}
              {def.matrixLatex && (
                <div style={{
                  padding: "8px 14px",
                  fontSize: 11,
                  color: colors.textSecondary,
                  fontFamily: fonts.mono,
                  borderBottom: `1px solid ${colors.border}`,
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                  lineHeight: 1.6,
                }}>
                  {formatMatrix(def.matrixLatex)}
                </div>
              )}

              {/* Qiskit name */}
              <div style={{
                padding: "6px 14px",
                fontSize: 10,
                color: colors.textTertiary,
                fontFamily: fonts.mono,
                display: "flex",
                gap: 12,
              }}>
                <span>Qiskit: <span style={{ color: colors.textSecondary }}>{def.qiskitName}</span></span>
                <span>Qubits: <span style={{ color: colors.textSecondary }}>{def.numQubits}</span></span>
                {def.parametric && <span style={{ color: colors.warning }}>parametric</span>}
              </div>

              {/* Glossary link */}
              {def.glossaryTermId && (
                <div style={{
                  padding: "6px 14px",
                  borderTop: `1px solid ${colors.border}`,
                  fontSize: 11,
                  color: colors.accentLight,
                  fontFamily: fonts.sans,
                }}>
                  Glossary: {def.glossaryTermId}
                </div>
              )}
            </div>
          </>
        );
      })()}
    </>
  );
}
