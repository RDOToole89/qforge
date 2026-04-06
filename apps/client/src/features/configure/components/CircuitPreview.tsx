"use dom";

import React, { useState, useEffect, useRef } from "react";
import { CircuitViewer } from "@/src/features/circuit-builder/components/CircuitViewer";
import UnifiedBlochSphere from "@/src/features/bloch-sphere/components/UnifiedBlochSphere";
import type { BlochDot } from "@/src/features/bloch-sphere/data/stateBlochConfigs";
import type { Circuit } from "@/src/features/circuit-builder/types";
import { colors, radii } from "@/src/theme";

/** Bloch sphere representations for each state type (theoretical, noiseless). */
const STATE_BLOCH: Record<string, { dots: BlochDot[]; caption: string; explanation: string }> = {
  GHZ: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: "#818cf8", label: "mixed" }],
    caption: "Each qubit: maximally mixed",
    explanation: "GHZ entanglement is global \u2014 individual qubits appear as I/2 (center of Bloch ball). The structure lives in multi-qubit correlations, not single-qubit states.",
  },
  W: {
    dots: [{ rx: 0, ry: 0, rz: 0.33, color: "#34d399", label: "partial" }],
    caption: "Each qubit: partially mixed",
    explanation: "W state qubits are partially mixed with a bias toward |0\u27E9. Unlike GHZ, losing one qubit preserves entanglement among the rest.",
  },
  CLUSTER: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: "#f59e0b", label: "mixed" }],
    caption: "Each qubit: maximally mixed",
    explanation: "Cluster state qubits are maximally mixed individually. The entanglement structure follows the graph topology (nearest-neighbor CZ bonds).",
  },
  BELL: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: "#ec4899", label: "mixed" }],
    caption: "Each qubit: maximally mixed",
    explanation: "Bell pair qubits are maximally entangled \u2014 each appears as I/2. All information is in the 2-qubit correlation.",
  },
  SUPERPOSITION: {
    dots: [{ rx: 1, ry: 0, rz: 0, color: "#6366f1", label: "|+\u27E9" }],
    caption: "Pure state: |+\u27E9",
    explanation: "Equal superposition of |0\u27E9 and |1\u27E9. Each qubit sits on the equator of the Bloch sphere (X-axis). No entanglement \u2014 product state.",
  },
};

interface CircuitPreviewProps {
  /** Serialized ExperimentConfig JSON to POST to /api/experiments/preview */
  configJson: string;
}

interface PreviewResponse {
  circuit: Circuit;
  diagram: string;
  stats: { depth: number; num_gates: number; num_qubits: number };
}

const DEV_URL = "http://localhost:8000/api";

export function CircuitPreview({ configJson }: CircuitPreviewProps) {
  const [circuitData, setCircuitData] = useState<Circuit | null>(null);
  const [stats, setStats] = useState<PreviewResponse["stats"] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [collapsed, setCollapsed] = useState(false);

  // Parse state type from config for Bloch sphere display
  const parsedConfig = (() => {
    try { return JSON.parse(configJson); }
    catch { return {}; }
  })();
  const stateType: string = parsedConfig.state_type ?? "GHZ";
  const blochConfig = STATE_BLOCH[stateType] ?? null;

  const fetchPreview = () => {
    setLoading(true);
    setError(null);
    fetch(`${DEV_URL}/experiments/preview`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: configJson,
    })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: PreviewResponse) => {
        setCircuitData(data.circuit);
        setStats(data.stats);
      })
      .catch((e) => setError(e.message ?? "Preview failed"))
      .finally(() => setLoading(false));
  };

  // Auto-fetch on config change (debounced 500ms)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(fetchPreview, 500);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [configJson]);

  return (
    <div
      style={{
        marginTop: 20,
        background: colors.bg.surface,
        borderRadius: radii.md,
        border: `1px solid ${colors.border}`,
        overflow: "visible",
      }}
    >
      {/* Header */}
      <div
        onClick={() => setCollapsed((v) => !v)}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 14px",
          cursor: "pointer",
          userSelect: "none",
        }}
      >
        <span
          style={{ color: colors.text.primary, fontSize: 14, fontWeight: 700 }}
        >
          Circuit Preview
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {stats && (
            <span
              style={{
                color: colors.text.tertiary,
                fontSize: 11,
                fontFamily: "SpaceMono, monospace",
              }}
            >
              {stats.depth}d / {stats.num_gates}g / {stats.num_qubits}q
            </span>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              fetchPreview();
            }}
            style={{
              padding: "3px 8px",
              borderRadius: 6,
              background: `${colors.accent.base}18`,
              border: `1px solid ${colors.accent.base}30`,
              color: colors.accent.base,
              fontSize: 10,
              fontWeight: 600,
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            Refresh
          </button>
          <span style={{ color: colors.text.tertiary, fontSize: 12 }}>
            {collapsed ? "\u25B8" : "\u25BE"}
          </span>
        </span>
      </div>

      {/* Body */}
      {!collapsed && (
        <div style={{ padding: "0 14px 14px" }}>
          {loading && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "12px 0",
              }}
            >
              <span
                style={{ color: colors.text.secondary, fontSize: 12 }}
              >
                Generating circuit...
              </span>
            </div>
          )}

          {error && (
            <div style={{ color: colors.status.error, fontSize: 12, padding: "8px 0" }}>
              {error}
            </div>
          )}

          {!loading && !error && circuitData && (
            <div style={{ display: "flex", gap: 14, alignItems: "stretch", minHeight: 280 }}>
              <div style={{ flex: 1, minWidth: 0, overflow: "auto" }}>
                <CircuitViewer circuit={circuitData} />
              </div>
              {blochConfig && (
                <div
                  style={{
                    width: "25%",
                    flexShrink: 0,
                    position: "relative",
                    background: `${blochConfig.dots[0]?.color ?? colors.accent.base}06`,
                    border: `1px solid ${blochConfig.dots[0]?.color ?? colors.accent.base}15`,
                    borderRadius: 10,
                    overflow: "hidden",
                  }}
                >
                  {/* Vertically + horizontally centered content */}
                  <div
                    style={{
                      position: "absolute",
                      top: "50%",
                      left: "50%",
                      transform: "translate(-50%, -50%)",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      gap: 8,
                      width: "90%",
                    }}
                  >
                    <UnifiedBlochSphere
                      mode="glossary"
                      dots={blochConfig.dots}
                      caption={blochConfig.caption}
                      size={160}
                    />
                    <div style={{ color: colors.text.primary, fontSize: 14, fontWeight: 600, textAlign: "center" }}>
                      Qubit State
                    </div>
                    <div style={{ color: colors.text.secondary, fontSize: 12, lineHeight: 1.6, textAlign: "center" }}>
                      {blochConfig.explanation}
                    </div>
                    <div
                      onClick={() => { window.location.hash = "#visualizer"; }}
                      style={{
                        color: colors.accent.base,
                        fontSize: 12,
                        fontWeight: 600,
                        cursor: "pointer",
                        paddingTop: 4,
                      }}
                    >
                      Open in Visualizer \u2192
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {!loading && !error && !circuitData && (
            <div
              onClick={fetchPreview}
              style={{
                padding: 10,
                textAlign: "center",
                color: colors.accent.base,
                fontSize: 13,
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Generate Preview
            </div>
          )}
        </div>
      )}
    </div>
  );
}
