'use dom';

import React from "react";
import type { FingerprintEntry } from "../types";

interface FingerprintViewerProps {
  entries: FingerprintEntry[];
  stateColor: string;
}

export default function FingerprintViewer({
  entries,
  stateColor,
}: FingerprintViewerProps) {
  return (
    <div style={{ fontFamily: "monospace", fontSize: 12 }}>
      <div
        style={{
          color: "#94a3b8",
          marginBottom: 8,
          fontWeight: 600,
          fontSize: 13,
        }}
      >
        Noise Fingerprint
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "40px 1fr 1fr",
          gap: 2,
          fontSize: 10,
          color: "#64748b",
          marginBottom: 4,
        }}
      >
        <div />
        <div style={{ textAlign: "center" }}>Clean</div>
        <div style={{ textAlign: "center" }}>Noisy</div>
      </div>
      {entries.map((e) => {
        const delta = e.noisy - e.clean;
        const deltaColor =
          Math.abs(delta) < 0.01
            ? "#64748b"
            : delta > 0
              ? "#44ff88"
              : "#ff4466";

        return (
          <div
            key={e.label}
            style={{
              display: "grid",
              gridTemplateColumns: "40px 1fr 1fr",
              gap: 2,
              padding: "3px 0",
              borderBottom: "1px solid rgba(255,255,255,0.03)",
            }}
          >
            <div
              style={{
                color: "#94a3b8",
                textTransform: "uppercase",
                fontSize: 10,
              }}
            >
              {e.label}
            </div>
            <div style={{ textAlign: "center", color: stateColor }}>
              {e.clean.toFixed(3)}
            </div>
            <div style={{ textAlign: "center", color: deltaColor }}>
              {e.noisy.toFixed(3)}
              <span style={{ fontSize: 9, marginLeft: 4, opacity: 0.6 }}>
                ({delta >= 0 ? "+" : ""}
                {delta.toFixed(3)})
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
