/** Shared style constants for the circuit builder (used inside 'use dom' context) */

export const colors = {
  bg: "#0a0c14",
  surface: "#131620",
  card: "#1a1e2e",
  border: "#2a2f42",
  wire: "#3a4060",
  wireActive: "#6366f1",
  text: "#e2e8f0",
  textSecondary: "#94a3b8",
  textTertiary: "#64748b",
  accent: "#6366f1",
  accentLight: "#818cf8",
  accentDim: "#312e81",
  success: "#22c55e",
  warning: "#f59e0b",
  danger: "#ef4444",
  dropZone: "rgba(99, 102, 241, 0.15)",
  dropZoneBorder: "rgba(99, 102, 241, 0.4)",
} as const;

export const layout = {
  /** Vertical spacing between qubit wires */
  wireSpacing: 56,
  /** Horizontal width of each moment column */
  momentWidth: 64,
  /** Width of qubit labels on the left */
  labelWidth: 52,
  /** Size of gate blocks (square) */
  gateSize: 40,
  /** Padding around the canvas */
  padding: 16,
  /** Radius of control dots on multi-qubit gates */
  controlDotRadius: 5,
  /** Size of the target symbol (CNOT cross-circle) */
  targetRadius: 12,
} as const;

export const fonts = {
  mono: "'IBM Plex Mono', 'SF Mono', 'Fira Code', monospace",
  sans: "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif",
} as const;

/** Compute the x position of a moment column */
export function momentX(momentIndex: number): number {
  return layout.labelWidth + layout.padding + momentIndex * layout.momentWidth + layout.momentWidth / 2;
}

/** Compute the y position of a qubit wire */
export function wireY(qubitIndex: number): number {
  return layout.padding + 20 + qubitIndex * layout.wireSpacing + layout.wireSpacing / 2;
}

/** Compute the total SVG width for a given number of moments */
export function canvasWidth(numMoments: number): number {
  return layout.labelWidth + layout.padding * 2 + Math.max(numMoments + 2, 4) * layout.momentWidth;
}

/** Compute the total SVG height for a given number of qubits */
export function canvasHeight(numQubits: number): number {
  return layout.padding * 2 + 20 + numQubits * layout.wireSpacing;
}
