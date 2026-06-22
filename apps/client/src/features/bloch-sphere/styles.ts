import type React from "react";

import { chrome } from "../../design/tokens";

/**
 * Build an `rgba()` string from a hex design-token color plus a (possibly
 * dynamic) alpha in [0, 1]. Lets data-driven tints (heatmaps, similarity
 * grids) keep their color single-sourced from tokens while varying opacity.
 */
export const rgba = (hex: string, a: number): string => {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${a})`;
};

export const LS: React.CSSProperties = {
  fontSize: "10px", color: chrome.text.tertiary, letterSpacing: "0.8px",
  fontWeight: 600, marginBottom: "6px",
};

export const bdr = `1px solid ${chrome.border.subtle}`;

export const cS = (c: string): React.CSSProperties => ({
  background: `${c}08`, border: `1px solid ${c}18`, borderRadius: "8px",
  padding: "10px 12px", fontSize: "11.5px", lineHeight: "1.55", color: chrome.text.secondary,
});

export const cT = (c: string): React.CSSProperties => ({
  color: c, fontWeight: 600, fontSize: "10px", letterSpacing: "0.5px", marginBottom: "5px",
});
