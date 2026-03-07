'use dom';

import { useMemo } from "react";
import { generate2QFromState, apply2QNoise } from "../math";
import type { ProbeStateConfig, TopologyConfig } from "../types";

interface CorrelatorBarsProps {
  stateCfg: ProbeStateConfig;
  topo: TopologyConfig;
  strength: number;
}

export default function CorrelatorBars({ stateCfg, topo, strength }: CorrelatorBarsProps) {
  const pts = useMemo(() => generate2QFromState(stateCfg, 100), [stateCfg]);
  const noised = apply2QNoise(pts, topo, strength);

  const avgOrig = { zi: 0, iz: 0, zz: 0 };
  const avgNoise = { zi: 0, iz: 0, zz: 0 };
  pts.forEach((p) => { avgOrig.zi += p.zi; avgOrig.iz += p.iz; avgOrig.zz += p.zz; });
  noised.forEach((p) => { avgNoise.zi += p.zi; avgNoise.iz += p.iz; avgNoise.zz += p.zz; });

  const n = pts.length;
  const delta = {
    zi: avgNoise.zi / n - avgOrig.zi / n,
    iz: avgNoise.iz / n - avgOrig.iz / n,
    zz: avgNoise.zz / n - avgOrig.zz / n,
  };

  const bars = [
    { label: "\u0394\u27E8ZI\u27E9", value: delta.zi, color: "#ff4466" },
    { label: "\u0394\u27E8IZ\u27E9", value: delta.iz, color: "#44ff88" },
    { label: "\u0394\u27E8ZZ\u27E9", value: delta.zz, color: "#4488ff" },
  ];
  const mx = Math.max(...bars.map((b) => Math.abs(b.value)), 0.001);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
      {bars.map((b) => (
        <div key={b.label} style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <div style={{ width: "44px", fontSize: "10px", fontFamily: "monospace", color: b.color, textAlign: "right" }}>
            {b.label}
          </div>
          <div style={{
            flex: 1, height: "12px", background: "rgba(255,255,255,0.03)",
            borderRadius: "3px", position: "relative", overflow: "hidden",
          }}>
            <div style={{
              position: "absolute", left: "50%", top: 0, bottom: 0,
              width: "1px", background: "rgba(255,255,255,0.1)",
            }} />
            <div style={{
              position: "absolute", left: "50%", top: 0, bottom: 0,
              width: `${(Math.abs(b.value) / mx) * 50}%`,
              background: b.color, opacity: 0.5, borderRadius: "2px",
              transform: b.value >= 0 ? "none" : "translateX(-100%)",
            }} />
          </div>
          <div style={{ width: "48px", fontSize: "9px", fontFamily: "monospace", color: "#667", textAlign: "right" }}>
            {b.value.toFixed(4)}
          </div>
        </div>
      ))}
    </div>
  );
}
