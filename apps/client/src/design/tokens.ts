/**
 * Design tokens — single source of truth.
 *
 * This module is plain TypeScript (only object literals + `as const` + type
 * exports). It is consumed by BOTH:
 *   1. `tailwind.config.ts` — flattened into the NativeWind theme so utility
 *      classes (`bg-surface`, `text-secondary`, …) resolve to these values.
 *   2. Runtime JS/TS code — React Native `StyleSheet` and the `'use dom'`
 *      inline-CSS features import the raw values directly.
 *
 * Because both paths import THIS file, there is exactly one copy of every
 * value. Never hard-code these hex/number literals elsewhere.
 */

// ───────────────────────────────────────────────────────────────────────────
// Colors
// ───────────────────────────────────────────────────────────────────────────

/**
 * `chrome` — application UI palette (the "shell": backgrounds, text, borders,
 * accents, status colors). These read as dark-theme surfaces and slate text.
 */
export const chrome = {
  bg: {
    primary: "#0f172a",
    surface: "#1e293b",
    elevated: "#283548",
  },
  text: {
    primary: "#e2e8f0",
    secondary: "#94a3b8",
    tertiary: "#64748b",
  },
  border: {
    default: "#334155",
    subtle: "rgba(255,255,255,0.06)",
  },
  accent: {
    base: "#6366f1",
    dark: "#4f46e5",
    light: "#818cf8",
  },
  status: {
    error: "#ef4444",
    warning: "#f59e0b",
    success: "#22c55e",
    info: "#6366f1",
  },
} as const;

/**
 * `viz` — physics / data-visualization palette. Distinct from `chrome` so that
 * data colors never drift into UI chrome (and vice versa). `series` is the
 * ordered categorical scale for per-qubit / per-series coloring.
 */
export const viz = {
  // ── Primary data hues (brand identity for the bloch-sphere viz) ──
  orange: "#ff9933",
  cyan: "#44c8ff",
  pink: "#f472b6",
  violet: "#a78bfa",
  sky: "#38bdf8",
  green: "#44ff88",

  // ── Extended categorical palette ──
  // Single source for per-state Bloch dots, per-qubit series, correlator
  // axes, and channel/topology accents across the bloch-sphere feature.
  // Distinct hues chosen so adjacent data points stay legible. Neutral
  // tones reuse chrome text neutrals so greys are never duplicated.
  indigo: "#818cf8", // generic mixed / probability-amplitude dots
  emerald: "#34d399", // W-state / "good" outcome dots
  amber: "#fb923c", // cluster / graph-state dots
  aqua: "#44ddff", // Bell-state / qubit-series cyan
  purple: "#b48cff", // cluster-state / qubit-series violet
  rose: "#ff4466", // superposition / ZI correlator / qubit-series red
  blue: "#4488ff", // ZZ correlator / Z-axis / blue map accent
  blueDim: "#3366aa", // original (pre-map) Bloch point cloud
  magenta: "#cc44ff", // state×topology / star-topology accent
  yellow: "#ffdd44", // qubit-series yellow
  teal: "#44ffdd", // qubit-series teal
  rosePink: "#ff88cc", // qubit-series light pink
  muted: chrome.text.secondary, // neutral / "mixed" / "null" reference dots
  mutedDim: chrome.text.tertiary, // dimmed reference dots

  // Extra categorical hues used by the circuit-builder amplitude-evolution
  // graph (per-basis-state traces). Distinct from the brighter Bloch hues
  // above; kept here so the amplitude scale has a single source.
  cyanDeep: "#06b6d4",
  lime: "#84cc16",
  crimson: "#e11d48",
  azure: "#0ea5e9",
  emeraldDeep: "#10b981", // glossary "states" category accent (deeper than `emerald`)

  series: ["#6366f1", "#f472b6", "#44c8ff", "#ff9933", "#a78bfa", "#44ff88"],

  /**
   * Categorical colors keyed by quantum gate family. Gate identity is a
   * data-visualization concern (not UI chrome), so the gate palette lives here
   * as the single source consumed by the circuit-builder gate library.
   */
  gate: {
    indigo: "#6366f1",
    red: "#ef4444",
    green: "#22c55e",
    blue: "#3b82f6",
    violet: "#8b5cf6",
    purple: "#a855f7",
    orange: "#f97316",
    yellow: "#eab308",
    teal: "#14b8a6",
    pink: "#ec4899",
    amber: "#f59e0b",
  },
} as const;

// ───────────────────────────────────────────────────────────────────────────
// Spacing & radii
// ───────────────────────────────────────────────────────────────────────────

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  "2xl": 24,
  "3xl": 32,
} as const;

export const radii = {
  xs: 2,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  pill: 999,
} as const;

// ───────────────────────────────────────────────────────────────────────────
// Typography
// ───────────────────────────────────────────────────────────────────────────

/** Numeric font weights (CSS/RN compatible). */
export const fontWeight = {
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
} as const;

/**
 * Semantic type scale. Each entry carries its pixel `size`, a paired
 * `lineHeight`, and a default `weight`. Use these names (`body`, `label`,
 * `heading`, …) instead of raw pixel sizes so type stays consistent.
 */
export const fontSize = {
  captionXs: { size: 9, lineHeight: 12, weight: fontWeight.regular },
  caption: { size: 10, lineHeight: 14, weight: fontWeight.regular },
  bodySm: { size: 11, lineHeight: 16, weight: fontWeight.regular },
  body: { size: 12, lineHeight: 18, weight: fontWeight.regular },
  bodyLg: { size: 13, lineHeight: 18, weight: fontWeight.regular },
  label: { size: 14, lineHeight: 20, weight: fontWeight.medium },
  headingSm: { size: 16, lineHeight: 22, weight: fontWeight.semibold },
  heading: { size: 18, lineHeight: 24, weight: fontWeight.semibold },
  headingLg: { size: 24, lineHeight: 30, weight: fontWeight.bold },
  display: { size: 28, lineHeight: 34, weight: fontWeight.bold },
} as const;

export const fontFamily = {
  mono: "IBM Plex Mono, ui-monospace, SFMono-Regular, monospace",
  sans: "IBM Plex Sans, system-ui, -apple-system, sans-serif",
} as const;

// ───────────────────────────────────────────────────────────────────────────
// Shadows (React Native elevation objects)
// ───────────────────────────────────────────────────────────────────────────

/**
 * Elevation presets as React Native shadow style objects. For the web/Tailwind
 * `boxShadow` equivalents see `tailwind.config.ts`, which derives CSS strings
 * from these same numbers.
 */
export const shadows = {
  level1: {
    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.18,
    shadowRadius: 2,
    elevation: 1,
  },
  level2: {
    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.22,
    shadowRadius: 6,
    elevation: 3,
  },
  level3: {
    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.28,
    shadowRadius: 12,
    elevation: 6,
  },
} as const;

// ───────────────────────────────────────────────────────────────────────────
// Aggregate + derived types
// ───────────────────────────────────────────────────────────────────────────

export const tokens = {
  chrome,
  viz,
  spacing,
  radii,
  fontWeight,
  fontSize,
  fontFamily,
  shadows,
} as const;

export type Tokens = typeof tokens;

export type ChromeBgColor = keyof typeof chrome.bg;
export type ChromeTextColor = keyof typeof chrome.text;
export type ChromeBorderColor = keyof typeof chrome.border;
export type ChromeAccentColor = keyof typeof chrome.accent;
export type ChromeStatusColor = keyof typeof chrome.status;

export type VizColor = Exclude<keyof typeof viz, "series">;

export type SpacingToken = keyof typeof spacing;
export type RadiusToken = keyof typeof radii;
export type FontSizeToken = keyof typeof fontSize;
export type FontWeightToken = keyof typeof fontWeight;
export type FontFamilyToken = keyof typeof fontFamily;
export type ShadowToken = keyof typeof shadows;

export default tokens;
