'use dom';

import { chrome, viz } from "@/src/design/tokens";
import { rgba } from "../styles";
import type { RuntimeChannel } from "../types";

interface PTMHeatmapProps {
  runtimeCh: Record<string, RuntimeChannel>;
  channel: string;
  strength: number;
  /** When provided, render this matrix directly instead of computing from channel */
  rawMatrix?: number[][];
}

const LABELS = ["I", "X", "Y", "Z"];
const LABEL_COLORS = [chrome.text.secondary, viz.rose, viz.green, viz.blue];

export default function PTMHeatmap({ runtimeCh, channel, strength, rawMatrix }: PTMHeatmapProps) {
  const ch = runtimeCh[channel];
  if (!ch && !rawMatrix) return null;

  const ptm = rawMatrix ?? ch!.ptm(strength);
  const mx = Math.max(...ptm.flat().map(Math.abs), 0.01);

  const bg = (v: number): string => {
    const t = v / mx;
    if (t > 0.01) return rgba(viz.orange, Math.min(t * 0.7, 0.65));
    if (t < -0.01) return rgba(viz.blue, Math.min(Math.abs(t) * 0.7, 0.65));
    return chrome.border.subtle;
  };

  return (
    <div>
      <div style={{ display: "flex", marginLeft: "28px" }}>
        {LABELS.map((l, i) => (
          <div key={l} style={{
            width: "42px", textAlign: "center", fontSize: "10px",
            color: LABEL_COLORS[i], fontFamily: "monospace", fontWeight: 600,
          }}>{l}</div>
        ))}
      </div>
      {ptm.map((row, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center" }}>
          <div style={{
            width: "28px", fontSize: "10px", textAlign: "right", paddingRight: "5px",
            color: LABEL_COLORS[i], fontFamily: "monospace", fontWeight: 600,
          }}>{LABELS[i]}</div>
          {row.map((v, j) => (
            <div key={j} style={{
              width: "42px", height: "28px", display: "flex", alignItems: "center", justifyContent: "center",
              background: bg(v), borderRadius: "3px", margin: "1px",
              fontSize: "10px", fontFamily: "monospace",
              color: Math.abs(v) > 0.25 ? chrome.text.primary : chrome.text.tertiary,
            }}>
              {Math.abs(v) > 0.005 ? v.toFixed(2) : ""}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
