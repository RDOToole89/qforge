'use dom';

import { useState, useEffect } from "react";
import { chrome, viz } from "@/src/design/tokens";
import { bdr, rgba } from "../styles";
import { DEFAULT_CONFIG } from "../config";
import type { BlochConfig } from "../types";

interface ConfigEditorProps {
  config: BlochConfig;
  onUpdate: (config: BlochConfig) => void;
  onClose: () => void;
}

type TabKey = "states" | "channels" | "data" | "topologies";

const HINTS: Record<TabKey, string> = {
  states: 'Define probe states with bloch: {rx, ry, rz}, correlators: {zi, iz, zz, xx, yy}, uniform: bool',
  channels: 'Define channels with blochMap: {rx, ry, rz} expressions. Vars: rx, ry, rz, p, sqrt()',
  data: 'Array of {label, noiseStrength, topology, fingerprint: [15 floats]}',
  topologies: 'Define 2Q topologies with corrGrowXX/YY/ZZ, singleQubitDecay',
};

export default function ConfigEditor({ config, onUpdate, onClose }: ConfigEditorProps) {
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<TabKey>("states");

  useEffect(() => {
    const sections: Record<TabKey, unknown> = {
      states: config.states,
      channels: config.channels,
      data: config.experimentalData,
      topologies: config.topologies,
    };
    setText(JSON.stringify(sections[tab] ?? {}, null, 2));
  }, [tab, config]);

  const apply = () => {
    try {
      const parsed = JSON.parse(text);
      const updated = { ...config };
      if (tab === "states") updated.states = parsed;
      else if (tab === "channels") updated.channels = parsed;
      else if (tab === "data") updated.experimentalData = parsed;
      else updated.topologies = parsed;
      setError(null);
      onUpdate(updated);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Parse error");
    }
  };

  const exportCfg = () => {
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "bloch-cptp-config.json";
    a.click();
  };

  const importCfg = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = (e: Event) => {
      const target = e.target as HTMLInputElement;
      const file = target.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        try {
          onUpdate(JSON.parse(ev.target?.result as string));
          setError(null);
        } catch (err: unknown) {
          setError(err instanceof Error ? err.message : "Parse error");
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  return (
    <div
      style={{
        position: "fixed", inset: 0, zIndex: 100,
        background: rgba(chrome.bg.primary, 0.7),
        display: "flex", alignItems: "center", justifyContent: "center",
      }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div style={{
        width: "720px", maxHeight: "85vh", background: chrome.bg.surface,
        border: `1px solid ${chrome.border.default}`, borderRadius: "12px",
        display: "flex", flexDirection: "column", overflow: "hidden",
      }}>
        {/* Header */}
        <div style={{
          padding: "12px 16px", borderBottom: bdr,
          display: "flex", alignItems: "center", gap: "10px",
        }}>
          <span style={{ fontSize: "14px", fontWeight: 600, color: chrome.text.primary }}>Config</span>
          <div style={{
            display: "flex", gap: "3px",
            background: chrome.border.subtle, borderRadius: "6px", padding: "2px",
          }}>
            {(["states", "channels", "data", "topologies"] as TabKey[]).map((t) => (
              <button key={t} onClick={() => setTab(t)} style={{
                padding: "4px 10px", borderRadius: "4px", border: "none",
                fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
                background: tab === t ? `${viz.orange}26` : "transparent",
                color: tab === t ? viz.orange : chrome.text.tertiary,
              }}>
                {t === "data" ? "Exp. Data" : t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
          <div style={{ flex: 1 }} />
          <button onClick={onClose} style={{
            background: "none", border: "none", color: chrome.text.tertiary,
            fontSize: "18px", cursor: "pointer",
          }}>x</button>
        </div>

        {/* Hint */}
        <div style={{ padding: "6px 16px 0", fontSize: "11px", color: chrome.text.tertiary, lineHeight: "1.5" }}>
          {HINTS[tab]}
        </div>

        {/* Editor */}
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          spellCheck={false}
          style={{
            flex: 1, margin: "10px 16px", padding: "12px",
            background: rgba(chrome.bg.primary, 0.3), border: `1px solid ${chrome.border.subtle}`,
            borderRadius: "8px", color: chrome.text.primary, fontFamily: "monospace",
            fontSize: "11px", lineHeight: "1.5", resize: "none", outline: "none",
            minHeight: "200px",
          }}
        />

        {/* Error */}
        {error && (
          <div style={{
            margin: "0 16px 8px", padding: "6px 10px",
            background: `${chrome.status.error}1a`, border: `1px solid ${chrome.status.error}33`,
            borderRadius: "6px", fontSize: "11px", color: chrome.status.error,
          }}>{error}</div>
        )}

        {/* Actions */}
        <div style={{
          padding: "10px 16px", borderTop: bdr,
          display: "flex", gap: "6px",
        }}>
          {([
            ["Apply", viz.orange, apply] as const,
            ["Export", viz.blue, exportCfg] as const,
            ["Import", viz.green, importCfg] as const,
          ]).map(([label, color, fn]) => (
            <button key={label} onClick={fn} style={{
              padding: "5px 12px", borderRadius: "5px",
              border: `1px solid ${color}44`, background: `${color}15`,
              color, fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
            }}>{label}</button>
          ))}
          <div style={{ flex: 1 }} />
          <button onClick={() => onUpdate(DEFAULT_CONFIG)} style={{
            padding: "5px 12px", borderRadius: "5px",
            border: `1px solid ${chrome.border.default}`,
            background: chrome.border.subtle,
            color: chrome.text.tertiary, fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
          }}>Reset</button>
        </div>
      </div>
    </div>
  );
}
