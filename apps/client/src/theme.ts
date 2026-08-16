/**
 * Semantic theme adapter.
 *
 * `theme.ts` is a THIN semantic layer over the design tokens
 * (`src/design/tokens.ts`). It re-shapes the raw `chrome` palette into the
 * bg/text/accent/border/status names the app's React Native StyleSheets
 * consume, and re-exports the spacing / radii / typography scales unchanged.
 *
 * There is exactly ONE source of color and scale truth: `tokens.ts`.
 * Do not hard-code hex/number literals here.
 */
import {
  chrome,
  spacing as spacingTokens,
  radii as radiiTokens,
  fontSize as fontSizeTokens,
  fontFamily as fontFamilyTokens,
  fontWeight as fontWeightTokens,
} from "./design/tokens";

export const colors = {
  bg:     { primary: chrome.bg.primary, surface: chrome.bg.surface, elevated: chrome.bg.elevated },
  text:   { primary: chrome.text.primary, secondary: chrome.text.secondary, tertiary: chrome.text.tertiary },
  accent: { base: chrome.accent.base, dark: chrome.accent.dark, light: chrome.accent.light },
  border: chrome.border.default,
  status: { error: chrome.status.error, warning: chrome.status.warning, success: chrome.status.success, info: chrome.status.info },
};

// Legacy scale shape mapped onto token values so existing StyleSheet consumers
// stay PIXEL-IDENTICAL (the new design-token scale is adopted intentionally when
// components migrate to NativeWind, not as a silent side effect of this adapter).
export const spacing = {
  xs: spacingTokens.xs, // 4
  sm: spacingTokens.sm, // 8
  md: spacingTokens.md, // 12
  lg: spacingTokens.lg, // 16
  xl: spacingTokens["2xl"], // 24 (legacy theme.spacing.xl)
};
export const radii = {
  sm: radiiTokens.md, // 8
  md: radiiTokens.lg, // 12
  lg: radiiTokens.xl, // 16
  pill: radiiTokens.pill, // 999
};

// Typography re-exports (single source: tokens.ts)
export const fontSize = fontSizeTokens;
export const fontFamily = fontFamilyTokens;
export const fontWeight = fontWeightTokens;
