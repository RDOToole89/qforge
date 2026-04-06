'use dom';

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
      <h1 style={{ margin: 0, fontSize: "15px", fontWeight: 600, color: "#e8eef6" }}>
        CPTP Maps — Bloch Sphere
      </h1>

      {/* Mode toggle */}
      <div style={{
        display: "flex", gap: "2px",
        background: "rgba(255,255,255,0.03)", borderRadius: "7px", padding: "2px",
      }}>
        {([
          { id: "builtin" as const, label: "Built-in" },
          { id: "experiment" as const, label: "Experiment" },
        ]).map((m) => (
          <button key={m.id} onClick={() => setMode(m.id)} style={{
            padding: "5px 11px", borderRadius: "5px", border: "none",
            background: mode === m.id ? "rgba(68,200,255,0.15)" : "transparent",
            color: mode === m.id ? "#44c8ff" : "#5a6a82",
            fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
            fontWeight: mode === m.id ? 600 : 400,
          }}>
            {m.label}
            {m.id === "experiment" && storedResultsCount > 0 && (
              <span style={{
                marginLeft: "4px", fontSize: "9px", padding: "1px 4px",
                borderRadius: "3px", background: "rgba(68,200,255,0.15)", color: "#44c8ff",
              }}>{storedResultsCount}</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab buttons */}
      <div style={{
        display: "flex", gap: "2px",
        background: "rgba(255,255,255,0.03)", borderRadius: "7px", padding: "2px",
      }}>
        {([
          { id: "single" as const, label: "1-Qubit" },
          { id: "multi" as const, label: "2-Qubit" },
          { id: "ptm" as const, label: "PTM" },
          { id: "data" as const, label: "Data" },
        ]).map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            padding: "5px 11px", borderRadius: "5px", border: "none",
            background: tab === t.id ? "rgba(255,153,51,0.15)" : "transparent",
            color: tab === t.id ? "#ff9933" : "#5a6a82",
            fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
            fontWeight: tab === t.id ? 600 : 400,
          }}>{t.label}</button>
        ))}
      </div>
      <div style={{ flex: 1 }} />
      {!isExp && (
        <button onClick={onConfigOpen} style={{
          padding: "5px 11px", borderRadius: "6px",
          border: "1px solid rgba(255,153,51,0.25)",
          background: "rgba(255,153,51,0.08)", color: "#ff9933",
          fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
        }}>Config</button>
      )}
    </div>
  );
}
