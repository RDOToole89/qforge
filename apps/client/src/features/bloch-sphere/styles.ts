import type React from "react";

import { chrome } from "../../design/tokens";

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
