import type { Config } from "tailwindcss";

import {
  chrome,
  viz,
  spacing,
  radii,
  fontSize,
  fontFamily,
  shadows,
} from "./src/design/tokens";

/**
 * NativeWind theme — derived entirely from `./src/design/tokens`.
 *
 * tailwindcss v3 loads this `.ts` config through its bundled `jiti`, so the TS
 * token module is imported directly: there is ONE source of truth, no
 * duplicated literals.
 *
 * ── Color class-naming scheme ──────────────────────────────────────────────
 * The nested token groups are flattened into a flat Tailwind color map. Each
 * key works with every color utility (`bg-`, `text-`, `border-`), but is named
 * for its INTENDED pairing:
 *
 *   Chrome backgrounds (pair with `bg-`):
 *     bg-base        chrome.bg.primary     #0f172a   (app canvas)
 *     bg-surface     chrome.bg.surface     #1e293b
 *     bg-elevated    chrome.bg.elevated    #283548
 *
 *   Chrome text/foreground (pair with `text-`):
 *     text-primary   chrome.text.primary   #e2e8f0
 *     text-secondary chrome.text.secondary #94a3b8
 *     text-tertiary  chrome.text.tertiary  #64748b
 *
 *   Borders (pair with `border-`):
 *     border-default chrome.border.default #334155
 *     border-subtle  chrome.border.subtle  rgba(255,255,255,0.06)
 *
 *   Accent (DEFAULT + variants → `bg-accent`, `text-accent-dark`, …):
 *     accent         chrome.accent.base    #6366f1
 *     accent-dark    chrome.accent.dark    #4f46e5
 *     accent-light   chrome.accent.light   #818cf8
 *
 *   Status (`text-error`, `bg-success`, …):
 *     error / warning / success / info
 *
 *   Visualization (data/physics — `text-viz-orange`, `bg-viz-cyan`, …):
 *     viz-orange / viz-cyan / viz-pink / viz-violet / viz-sky / viz-green
 */

const px = (n: number): string => `${n}px`;

// fontSize → Tailwind tuple form: [size, { lineHeight, fontWeight }]
const fontSizeTheme = Object.fromEntries(
  Object.entries(fontSize).map(([name, v]) => [
    name,
    [px(v.size), { lineHeight: px(v.lineHeight), fontWeight: String(v.weight) }],
  ]),
) as Config["theme"] & Record<string, unknown>;

// spacing / radii → px strings
const spacingTheme = Object.fromEntries(
  Object.entries(spacing).map(([k, v]) => [k, px(v)]),
);

const radiiTheme = Object.fromEntries(
  Object.entries(radii).map(([k, v]) => [
    k,
    v >= 999 ? "9999px" : px(v),
  ]),
);

// RN shadow objects → CSS box-shadow strings (web)
const boxShadowTheme = Object.fromEntries(
  Object.entries(shadows).map(([name, s]) => [
    name,
    `${px(s.shadowOffset.width)} ${px(s.shadowOffset.height)} ${px(
      s.shadowRadius,
    )} rgba(0,0,0,${s.shadowOpacity})`,
  ]),
);

const config: Config = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        // chrome backgrounds
        base: chrome.bg.primary,
        surface: chrome.bg.surface,
        elevated: chrome.bg.elevated,
        // chrome text
        primary: chrome.text.primary,
        secondary: chrome.text.secondary,
        tertiary: chrome.text.tertiary,
        // borders
        default: chrome.border.default,
        subtle: chrome.border.subtle,
        // accent
        accent: {
          DEFAULT: chrome.accent.base,
          dark: chrome.accent.dark,
          light: chrome.accent.light,
        },
        // status
        error: chrome.status.error,
        warning: chrome.status.warning,
        success: chrome.status.success,
        info: chrome.status.info,
        // visualization
        "viz-orange": viz.orange,
        "viz-cyan": viz.cyan,
        "viz-pink": viz.pink,
        "viz-violet": viz.violet,
        "viz-sky": viz.sky,
        "viz-green": viz.green,
      },
      fontSize: fontSizeTheme,
      spacing: spacingTheme,
      borderRadius: radiiTheme,
      fontFamily: {
        mono: fontFamily.mono.split(",").map((s) => s.trim()),
        sans: fontFamily.sans.split(",").map((s) => s.trim()),
      },
      boxShadow: boxShadowTheme,
    },
  },
  plugins: [],
};

export default config;
