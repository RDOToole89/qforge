'use dom';

import React from "react";
import type { CorrelatorSignature } from "../types";

interface CorrelatorBarsProps {
  clean: CorrelatorSignature;
  noisy: CorrelatorSignature;
  stateColor: string;
}

const CORRELATOR_KEYS: (keyof CorrelatorSignature)[] = [
  "zi",
  "iz",
  "zz",
  "xx",
  "yy",
  "xz",
  "zx",
];

export default function CorrelatorBars({
  clean,
  noisy,
  stateColor,
}: CorrelatorBarsProps) {
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
        Correlator Signature
      </div>
      {CORRELATOR_KEYS.map((key) => {
        const cleanVal = clean[key] ?? 0;
        const noisyVal = noisy[key] ?? 0;
        if (cleanVal === 0 && noisyVal === 0) return null;

        const barWidth = (v: number) =>
          `${Math.min(Math.abs(v) * 100, 100)}%`;

        return (
          <div key={key} style={{ marginBottom: 6 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                color: "#94a3b8",
                marginBottom: 2,
              }}
            >
              <span style={{ textTransform: "uppercase", fontSize: 10 }}>
                {String(key)}
              </span>
              <span style={{ fontSize: 10 }}>
                {cleanVal.toFixed(2)} {"\u2192"} {noisyVal.toFixed(2)}
              </span>
            </div>
            <div
              style={{
                position: "relative",
                height: 8,
                background: "rgba(255,255,255,0.05)",
                borderRadius: 4,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  left: cleanVal >= 0 ? "50%" : undefined,
                  right: cleanVal < 0 ? "50%" : undefined,
                  top: 0,
                  height: "100%",
                  width: barWidth(cleanVal),
                  background: stateColor,
                  opacity: 0.3,
                  borderRadius: 4,
                }}
              />
              <div
                style={{
                  position: "absolute",
                  left: noisyVal >= 0 ? "50%" : undefined,
                  right: noisyVal < 0 ? "50%" : undefined,
                  top: 0,
                  height: "100%",
                  width: barWidth(noisyVal),
                  background: stateColor,
                  opacity: 0.8,
                  borderRadius: 4,
                }}
              />
            </div>
          </div>
        );
      })}
      <div style={{ marginTop: 8, fontSize: 10, color: "#64748b" }}>
        <span
          style={{
            display: "inline-block",
            width: 10,
            height: 10,
            background: stateColor,
            opacity: 0.3,
            borderRadius: 2,
            marginRight: 4,
            verticalAlign: "middle",
          }}
        />
        Clean{" "}
        <span
          style={{
            display: "inline-block",
            width: 10,
            height: 10,
            background: stateColor,
            opacity: 0.8,
            borderRadius: 2,
            marginRight: 4,
            marginLeft: 8,
            verticalAlign: "middle",
          }}
        />
        Noisy
      </div>
    </div>
  );
}
