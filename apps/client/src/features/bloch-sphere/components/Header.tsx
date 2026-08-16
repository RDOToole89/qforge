'use dom';

import { chrome, viz } from "@/src/design/tokens";
import { bdr } from "../styles";

interface HeaderProps {
  mode: "builtin" | "experiment";
  setMode: (m: "builtin" | "experiment") => void;
  tab: "single" | "multi" | "ptm" | "data";
  setTab: (t: "single" | "multi" | "ptm" | "data") => void;
  storedResultsCount: number;
  isExp: boolean;
  onConfigOpen: () => void;
}

export default function Header({ mode, setMode, tab, setTab, storedResultsCount, isExp, onConfigOpen }: HeaderProps) {
  return (
    <div style={{
      padding: "10px 18px", borderBottom: bdr,
      display: "flex", alignItems: "center", gap: "10px", flexShrink: 0,
    }}>
      <h1 style={{ margin: 0, fontSize: "15px", fontWeight: 600, color: chrome.text.primary }}>
        CPTP Maps — Bloch Sphere
      </h1>

      {/* Mode toggle */}
      <div style={{
        display: "flex", gap: "2px",
        background: chrome.border.subtle, borderRadius: "7px", padding: "2px",
      }}>
        {([
          { id: "builtin" as const, label: "Built-in" },
          { id: "experiment" as const, label: "Experiment" },
        ]).map((m) => (
          <button key={m.id} onClick={() => setMode(m.id)} style={{
            padding: "5px 11px", borderRadius: "5px", border: "none",
            background: mode === m.id ? `${viz.cyan}26` : "transparent",
            color: mode === m.id ? viz.cyan : chrome.text.tertiary,
            fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
            fontWeight: mode === m.id ? 600 : 400,
          }}>
            {m.label}
            {m.id === "experiment" && storedResultsCount > 0 && (
              <span style={{
                marginLeft: "4px", fontSize: "9px", padding: "1px 4px",
                borderRadius: "3px", background: `${viz.cyan}26`, color: viz.cyan,
              }}>{storedResultsCount}</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab buttons */}
      <div style={{
        display: "flex", gap: "2px",
        background: chrome.border.subtle, borderRadius: "7px", padding: "2px",
      }}>
        {([
          { id: "single" as const, label: "1-Qubit" },
          { id: "multi" as const, label: "2-Qubit" },
          { id: "ptm" as const, label: "PTM" },
          { id: "data" as const, label: "Data" },
        ]).map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            padding: "5px 11px", borderRadius: "5px", border: "none",
            background: tab === t.id ? `${viz.orange}26` : "transparent",
            color: tab === t.id ? viz.orange : chrome.text.tertiary,
            fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
            fontWeight: tab === t.id ? 600 : 400,
          }}>{t.label}</button>
        ))}
      </div>
      <div style={{ flex: 1 }} />
      {!isExp && (
        <button onClick={onConfigOpen} style={{
          padding: "5px 11px", borderRadius: "6px",
          border: `1px solid ${viz.orange}40`,
          background: `${viz.orange}14`, color: viz.orange,
          fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
        }}>Config</button>
      )}
    </div>
  );
}
