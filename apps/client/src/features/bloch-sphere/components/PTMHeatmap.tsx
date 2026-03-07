'use dom';

import React from "react";

interface PTMHeatmapProps {
  matrix: number[][];
  channelName: string;
}

const LABELS = ["I", "X", "Y", "Z"];

function cellColor(v: number): string {
  const abs = Math.abs(v);
  if (v > 0.01) return `rgba(68, 221, 255, ${abs})`;
  if (v < -0.01) return `rgba(255, 100, 68, ${abs})`;
  return "rgba(255,255,255,0.03)";
}

export default function PTMHeatmap({ matrix, channelName }: PTMHeatmapProps) {
  return (
    <div style={{ fontFamily: "monospace", fontSize: 12 }}>
      <div
        style={{
          color: "#94a3b8",
          marginBottom: 6,
          fontWeight: 600,
          fontSize: 13,
        }}
      >
        PTM: {channelName}
      </div>
      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
        }}
      >
        <thead>
          <tr>
            <th style={{ width: 24 }} />
            {LABELS.map((l) => (
              <th
                key={l}
                style={{
                  color: "#64748b",
                  padding: "2px 6px",
                  textAlign: "center",
                  fontSize: 11,
                }}
              >
                {l}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={i}>
              <td
                style={{
                  color: "#64748b",
                  paddingRight: 4,
                  textAlign: "right",
                  fontSize: 11,
                }}
              >
                {LABELS[i]}
              </td>
              {row.map((v, j) => (
                <td
                  key={j}
                  style={{
                    background: cellColor(v),
                    color: Math.abs(v) > 0.3 ? "#fff" : "#94a3b8",
                    textAlign: "center",
                    padding: "4px 6px",
                    borderRadius: 3,
                    border: "1px solid rgba(255,255,255,0.05)",
                    fontSize: 11,
                    minWidth: 40,
                  }}
                >
                  {v.toFixed(2)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
