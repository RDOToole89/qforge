/** Shared style constants for the circuit builder (used inside 'use dom' context). */

import { chrome, fontFamily } from "../../design/tokens";

/** Convert a `#rrggbb` token value to an `rgba(...)` string at the given alpha. */
function withAlpha(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export const colors = {
  bg: chrome.bg.primary,
  surface: chrome.bg.surface,
  card: chrome.bg.elevated,
  border: chrome.border.default,
  wire: chrome.border.default,
  wireActive: chrome.accent.base,
  text: chrome.text.primary,
  textSecondary: chrome.text.secondary,
  textTertiary: chrome.text.tertiary,
  accent: chrome.accent.base,
  accentLight: chrome.accent.light,
  accentDim: chrome.accent.dark,
  success: chrome.status.success,
  warning: chrome.status.warning,
  danger: chrome.status.error,
  dropZone: withAlpha(chrome.accent.base, 0.15),
  dropZoneBorder: withAlpha(chrome.accent.base, 0.4),
} as const;

export const layout = {
  /** Vertical spacing between qubit wires */
  wireSpacing: 56,
  /** Horizontal width of each moment column */
  momentWidth: 72,
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
  mono: fontFamily.mono,
  sans: fontFamily.sans,
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
