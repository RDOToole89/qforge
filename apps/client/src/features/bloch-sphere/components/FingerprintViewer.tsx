'use dom';

import { chrome, viz } from "@/src/design/tokens";
import { rgba } from "../styles";
import type { ExperimentalDataEntry } from "../types";

interface FingerprintViewerProps {
  data: ExperimentalDataEntry[];
}

export default function FingerprintViewer({ data }: FingerprintViewerProps) {
  if (!data?.length) {
    return (
      <div style={{ fontSize: "11px", color: chrome.text.tertiary, fontStyle: "italic", padding: "10px" }}>
        No data loaded. Add entries in Config &rarr; Exp. Data.
      </div>
    );
  }

  const dot = (a: number[], b: number[]): number => a.reduce((s, v, i) => s + v * b[i], 0);
  const norm = (a: number[]): number => Math.sqrt(dot(a, a));
  const cos = (a: number[], b: number[]): number => {
    const n = norm(a) * norm(b);
    return n > 0 ? dot(a, b) / n : 0;
  };

  const norms = data.map((d) => norm(d.fingerprint));
  const mx = Math.max(...norms, 0.001);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
      <div style={{ fontSize: "10px", color: chrome.text.tertiary, fontWeight: 600 }}>NORMS</div>
      {data.map((d, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <div style={{
            width: "90px", fontSize: "9px", fontFamily: "monospace", color: chrome.text.secondary,
            overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
          }}>{d.label || `#${i}`}</div>
          <div style={{
            flex: 1, height: "11px", background: chrome.border.subtle,
            borderRadius: "3px", overflow: "hidden",
          }}>
            <div style={{
              width: `${(norms[i] / mx) * 100}%`, height: "100%",
              background: d.topology === "chain" ? viz.orange : d.topology === "star" ? viz.magenta : viz.aqua,
              borderRadius: "3px",
            }} />
          </div>
          <div style={{ width: "40px", fontSize: "9px", fontFamily: "monospace", color: chrome.text.tertiary, textAlign: "right" }}>
            {norms[i].toFixed(4)}
          </div>
        </div>
      ))}

      {data.length > 1 && data.length <= 12 && (
        <>
          <div style={{ fontSize: "10px", color: chrome.text.tertiary, fontWeight: 600, marginTop: "6px" }}>COSINE SIM</div>
          <div style={{ overflowX: "auto" }}>
            <div style={{ display: "inline-flex", flexDirection: "column", gap: "1px" }}>
              {data.map((_, i) => (
                <div key={i} style={{ display: "flex", gap: "1px" }}>
                  {data.map((_, j) => {
                    const c = cos(data[i].fingerprint, data[j].fingerprint);
                    return (
                      <div key={j} style={{
                        width: "22px", height: "18px", display: "flex", alignItems: "center", justifyContent: "center",
                        background: c > 0 ? rgba(viz.orange, c * 0.6) : rgba(viz.blue, Math.abs(c) * 0.6),
                        borderRadius: "2px", fontSize: "7px", fontFamily: "monospace",
                        color: Math.abs(c) > 0.5 ? chrome.text.primary : chrome.text.tertiary,
                      }}>
                        {i === j ? "" : c.toFixed(1)}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
