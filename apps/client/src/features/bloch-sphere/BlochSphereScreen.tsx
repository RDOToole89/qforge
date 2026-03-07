'use dom';

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { DEFAULT_CONFIG } from "./config";
import { buildRuntime, TAU } from "./math";
import type { BlochConfig } from "./types";
import BlochScene from "./components/BlochScene";
import TwoQubitScene from "./components/TwoQubitScene";
import PTMHeatmap from "./components/PTMHeatmap";
import CorrelatorBars from "./components/CorrelatorBars";
import FingerprintViewer from "./components/FingerprintViewer";
import ConfigEditor from "./components/ConfigEditor";

// Shared style constants
const LS: React.CSSProperties = {
  fontSize: "10px", color: "#5a6a82", letterSpacing: "0.8px",
  fontWeight: 600, marginBottom: "6px",
};
const bdr = "1px solid rgba(255,255,255,0.06)";

const cS = (c: string): React.CSSProperties => ({
  background: `${c}08`, border: `1px solid ${c}18`, borderRadius: "8px",
  padding: "10px 12px", fontSize: "11.5px", lineHeight: "1.55", color: "#7a8ea8",
});
const cT = (c: string): React.CSSProperties => ({
  color: c, fontWeight: 600, fontSize: "10px", letterSpacing: "0.5px", marginBottom: "5px",
});

export default function BlochSphereScreen() {
  const [config, setConfig] = useState<BlochConfig>(DEFAULT_CONFIG);
  const [showConfig, setShowConfig] = useState(false);
  const [tab, setTab] = useState<"single" | "multi" | "ptm" | "data">("single");
  const [channel, setChannel] = useState("depolarizing");
  const [stateKey, setStateKey] = useState("ghz");
  const [strength, setStrength] = useState(0.3);
  const [showOrig, setShowOrig] = useState(true);
  const [showTrans, setShowTrans] = useState(true);
  const [rotation, setRotation] = useState(0.6);
  const [isDragging, setIsDragging] = useState(false);
  const lastXRef = useRef(0);
  const [animating, setAnimating] = useState(false);
  const animRef = useRef<number>(0);
  const [activeTopo, setActiveTopo] = useState("all");
  const [viewMode, setViewMode] = useState<"full" | "state">("full");

  const runtimeCh = useMemo(() => buildRuntime(config.channels), [config.channels]);
  const stateCfg = config.states[stateKey] ?? Object.values(config.states)[0] ?? DEFAULT_CONFIG.states.ghz;
  const ch = runtimeCh[channel];

  // Sync selections when config changes
  useEffect(() => {
    if (!runtimeCh[channel]) {
      const f = Object.keys(runtimeCh)[0];
      if (f) setChannel(f);
    }
  }, [runtimeCh, channel]);
  useEffect(() => {
    if (!config.states[stateKey]) {
      const f = Object.keys(config.states)[0];
      if (f) setStateKey(f);
    }
  }, [config.states, stateKey]);

  // Animation
  const toggleAnim = useCallback(() => {
    if (animating) {
      setAnimating(false);
      cancelAnimationFrame(animRef.current);
      return;
    }
    setAnimating(true);
    let t = 0;
    const step = () => {
      t += 0.008;
      if (t > 1) t = 0;
      setStrength(0.5 - 0.5 * Math.cos(t * TAU));
      animRef.current = requestAnimationFrame(step);
    };
    animRef.current = requestAnimationFrame(step);
  }, [animating]);
  useEffect(() => () => cancelAnimationFrame(animRef.current), []);

  // Drag to rotate
  const onPD = useCallback((e: React.PointerEvent) => {
    setIsDragging(true);
    lastXRef.current = e.clientX;
  }, []);
  const onPM = useCallback((e: React.PointerEvent) => {
    if (!isDragging) return;
    setRotation((r) => r + (e.clientX - lastXRef.current) * 0.008);
    lastXRef.current = e.clientX;
  }, [isDragging]);
  const onPU = useCallback(() => setIsDragging(false), []);

  return (
    <div style={{
      width: "100vw", height: "100vh", background: "#08090e", color: "#c8d4e4",
      fontFamily: "'IBM Plex Sans', system-ui, sans-serif",
      display: "flex", flexDirection: "column", overflow: "hidden", userSelect: "none",
    }}>

      {/* ── HEADER ── */}
      <div style={{
        padding: "10px 18px", borderBottom: bdr,
        display: "flex", alignItems: "center", gap: "10px", flexShrink: 0,
      }}>
        <h1 style={{ margin: 0, fontSize: "15px", fontWeight: 600, color: "#e8eef6" }}>
          CPTP Maps — Bloch Sphere
        </h1>
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
        <button onClick={() => setShowConfig(true)} style={{
          padding: "5px 11px", borderRadius: "6px",
          border: "1px solid rgba(255,153,51,0.25)",
          background: "rgba(255,153,51,0.08)", color: "#ff9933",
          fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
        }}>Config</button>
      </div>

      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        {/* ── LEFT SIDEBAR ── */}
        <div style={{
          width: "250px", flexShrink: 0, padding: "12px 14px", borderRight: bdr,
          display: "flex", flexDirection: "column", gap: "10px", overflowY: "auto",
        }}>

          {/* STATE SELECTOR — always visible */}
          <div>
            <div style={LS}>PROBE STATE</div>
            {Object.entries(config.states).map(([key, st]) => (
              <button key={key} onClick={() => setStateKey(key)} style={{
                display: "flex", width: "100%", padding: "5px 9px", marginBottom: "2px",
                alignItems: "center", gap: "7px",
                background: stateKey === key ? `${st.color ?? "#ff9933"}18` : "rgba(255,255,255,0.02)",
                border: stateKey === key ? `1px solid ${st.color ?? "#ff9933"}44` : bdr,
                borderRadius: "5px",
                color: stateKey === key ? (st.color ?? "#ff9933") : "#667788",
                fontSize: "11.5px", fontFamily: "inherit", cursor: "pointer", textAlign: "left",
              }}>
                <span style={{
                  display: "inline-block", width: "7px", height: "7px", borderRadius: "50%",
                  background: st.color ?? "#888", flexShrink: 0,
                }} />
                <span>
                  <span style={{ fontWeight: 500 }}>{st.name}</span>
                  {st.zBasisSignal && (
                    <span style={{
                      marginLeft: "5px", fontSize: "9px", padding: "1px 5px", borderRadius: "3px",
                      background: st.zBasisSignal === "strong" ? "rgba(68,255,136,0.15)"
                        : st.zBasisSignal === "weak" ? "rgba(255,200,50,0.15)" : "rgba(255,68,68,0.12)",
                      color: st.zBasisSignal === "strong" ? "#44ff88"
                        : st.zBasisSignal === "weak" ? "#dda030" : "#ff6666",
                    }}>
                      {st.zBasisSignal === "strong" ? "Z\u2713" : st.zBasisSignal === "weak" ? "Z~" : "Z\u2717"}
                    </span>
                  )}
                </span>
              </button>
            ))}
          </div>

          {/* CHANNEL SELECTOR */}
          {(tab === "single" || tab === "ptm") && (
            <div>
              <div style={LS}>CHANNEL</div>
              {Object.entries(runtimeCh).map(([key, val]) => (
                <button key={key} onClick={() => setChannel(key)} style={{
                  display: "block", width: "100%", padding: "4px 9px", marginBottom: "2px",
                  background: channel === key ? "rgba(255,153,51,0.12)" : "rgba(255,255,255,0.02)",
                  border: channel === key ? "1px solid rgba(255,153,51,0.3)" : bdr,
                  borderRadius: "5px",
                  color: channel === key ? "#ff9933" : "#667788",
                  fontSize: "11px", fontFamily: "inherit", cursor: "pointer", textAlign: "left",
                }}>
                  <span style={{ fontWeight: 500 }}>{val.name}</span>
                  <span style={{ fontSize: "9.5px", opacity: 0.5, marginLeft: "5px" }}>{val.desc}</span>
                </button>
              ))}
            </div>
          )}

          {/* TOPOLOGY SELECTOR */}
          {tab === "multi" && (
            <div>
              <div style={LS}>TOPOLOGY</div>
              <button onClick={() => setActiveTopo("all")} style={{
                display: "block", width: "100%", padding: "4px 9px", marginBottom: "2px",
                background: activeTopo === "all" ? "rgba(255,153,51,0.12)" : "rgba(255,255,255,0.02)",
                border: activeTopo === "all" ? "1px solid rgba(255,153,51,0.3)" : bdr,
                borderRadius: "5px",
                color: activeTopo === "all" ? "#ff9933" : "#667788",
                fontSize: "11px", fontFamily: "inherit", cursor: "pointer", textAlign: "left",
              }}>All</button>
              {Object.entries(config.topologies).map(([key, val]) => (
                <button key={key} onClick={() => setActiveTopo(key)} style={{
                  display: "block", width: "100%", padding: "4px 9px", marginBottom: "2px",
                  background: activeTopo === key ? "rgba(180,140,255,0.12)" : "rgba(255,255,255,0.02)",
                  border: activeTopo === key ? "1px solid rgba(180,140,255,0.3)" : bdr,
                  borderRadius: "5px",
                  color: activeTopo === key ? "#b48cff" : "#667788",
                  fontSize: "11px", fontFamily: "inherit", cursor: "pointer", textAlign: "left",
                }}>{val.name}</button>
              ))}
            </div>
          )}

          {/* CONTROLS */}
          {tab !== "data" && (
            <>
              {tab === "single" && (
                <div style={{ display: "flex", gap: "4px" }}>
                  <button onClick={() => setViewMode(viewMode === "full" ? "state" : "full")} style={{
                    flex: 1, padding: "4px 8px", borderRadius: "5px",
                    fontSize: "10px", fontFamily: "inherit", cursor: "pointer",
                    background: viewMode === "state" ? "rgba(180,140,255,0.15)" : "rgba(255,255,255,0.02)",
                    border: viewMode === "state" ? "1px solid rgba(180,140,255,0.3)" : bdr,
                    color: viewMode === "state" ? "#b48cff" : "#556677",
                  }}>
                    {viewMode === "state" ? "\u25C9 State View" : "\u25CB Full Sphere"}
                  </button>
                  <button onClick={() => setShowOrig(!showOrig)} style={{
                    padding: "4px 8px", borderRadius: "5px",
                    fontSize: "10px", fontFamily: "inherit", cursor: "pointer",
                    background: showOrig ? "#3366aa22" : "rgba(255,255,255,0.02)",
                    border: showOrig ? "1px solid #3366aa44" : bdr,
                    color: showOrig ? "#3366aa" : "#556677",
                  }}>{"\u25CF"}</button>
                  <button onClick={() => setShowTrans(!showTrans)} style={{
                    padding: "4px 8px", borderRadius: "5px",
                    fontSize: "10px", fontFamily: "inherit", cursor: "pointer",
                    background: showTrans ? "#ff993322" : "rgba(255,255,255,0.02)",
                    border: showTrans ? "1px solid #ff993344" : bdr,
                    color: showTrans ? "#ff9933" : "#556677",
                  }}>{"\u25CF"}</button>
                </div>
              )}

              <div>
                <div style={LS}>
                  STRENGTH — <span style={{ color: "#ff9933" }}>{strength.toFixed(2)}</span>
                </div>
                <input
                  type="range" min="0" max="1" step="0.005"
                  value={strength}
                  onChange={(e) => {
                    if (animating) { setAnimating(false); cancelAnimationFrame(animRef.current); }
                    setStrength(parseFloat(e.target.value));
                  }}
                  style={{ width: "100%", accentColor: "#ff9933" }}
                />
              </div>

              <button onClick={toggleAnim} style={{
                padding: "5px 12px", borderRadius: "5px",
                fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
                background: animating ? "rgba(255,153,51,0.2)" : "rgba(255,255,255,0.04)",
                border: animating ? "1px solid rgba(255,153,51,0.4)" : bdr,
                color: animating ? "#ff9933" : "#667788",
              }}>
                {animating ? "\u23F8 Pause" : "\u25B6 Animate"}
              </button>
            </>
          )}

          <div style={cS("rgba(68,136,255)")}>
            <div style={cT("#4488ff")}>CONTRACTIVITY</div>
            CPTP maps can only shrink or preserve the Bloch ball. Orange \u2286 Blue.
          </div>
        </div>

        {/* ── CENTER 3D ── */}
        <div
          style={{
            flex: 1, position: "relative",
            cursor: isDragging ? "grabbing" : "grab",
          }}
          onPointerDown={onPD}
          onPointerMove={onPM}
          onPointerUp={onPU}
          onPointerLeave={onPU}
        >
          {(tab === "single" || tab === "ptm" || tab === "data") && (
            <BlochScene
              runtimeCh={runtimeCh}
              channel={channel}
              strength={strength}
              showOrig={showOrig}
              showTrans={showTrans}
              rotation={rotation}
              stateCfg={stateCfg}
              viewMode={viewMode}
            />
          )}
          {tab === "multi" && (
            <TwoQubitScene
              topoConfigs={config.topologies}
              activeTopo={activeTopo}
              strength={strength}
              rotation={rotation}
              stateCfg={stateCfg}
            />
          )}

          {/* Axis legend overlay */}
          <div style={{ position: "absolute", top: "10px", right: "14px", fontSize: "10px", color: "#3a4a5a" }}>
            {tab === "multi"
              ? <><span style={{ color: "#ff4466" }}>{"\u2501"}</span> \u27E8ZI\u27E9 <span style={{ color: "#44ff88" }}>{"\u2501"}</span> \u27E8IZ\u27E9 <span style={{ color: "#4488ff" }}>{"\u2501"}</span> \u27E8ZZ\u27E9</>
              : <><span style={{ color: "#ff4466" }}>{"\u2501"}</span> X <span style={{ color: "#44ff88" }}>{"\u2501"}</span> Y <span style={{ color: "#4488ff" }}>{"\u2501"}</span> Z</>
            }
          </div>

          {/* State name overlay */}
          <div style={{
            position: "absolute", top: "10px", left: "14px",
            fontSize: "11px", color: stateCfg.color ?? "#fff", fontWeight: 600,
          }}>
            {stateCfg.name}
            {stateCfg.uniform && (
              <span style={{ fontSize: "9px", opacity: 0.5, fontWeight: 400, marginLeft: "6px" }}>
                uniform Z-dist
              </span>
            )}
          </div>

          <div style={{ position: "absolute", bottom: "10px", left: "14px", fontSize: "9px", color: "#2a3a4a" }}>
            Drag to rotate
          </div>
        </div>

        {/* ── RIGHT SIDEBAR ── */}
        <div style={{
          width: "280px", flexShrink: 0, padding: "12px 14px", borderLeft: bdr,
          overflowY: "auto", display: "flex", flexDirection: "column", gap: "10px",
        }}>

          {/* STATE INFO — always shown */}
          <div style={{
            ...cS(`${stateCfg.color ?? "#ff9933"}`),
            background: `${stateCfg.color ?? "#ff9933"}0a`,
            border: `1px solid ${stateCfg.color ?? "#ff9933"}20`,
          }}>
            <div style={cT(stateCfg.color ?? "#ff9933")}>
              {stateCfg.name} — {
                stateCfg.zBasisSignal === "strong" ? "Z-BASIS SENSITIVE"
                : stateCfg.zBasisSignal === "weak" ? "Z-BASIS WEAK"
                : "Z-BASIS BLIND"
              }
            </div>
            <span style={{ color: "#a0b0c0" }}>{stateCfg.insight}</span>
          </div>

          {/* 1-QUBIT TAB: Channel info */}
          {tab === "single" && ch && (
            <>
              <div style={cS("rgba(255,153,51)")}>
                <div style={cT("#ff9933")}>KRAUS OPERATORS</div>
                <div style={{ fontFamily: "monospace", fontSize: "10px", color: "#8899bb", wordBreak: "break-all" }}>
                  {ch.kraus ?? "\u2014"}
                </div>
              </div>
              <div style={cS("rgba(68,136,255)")}>
                <div style={cT("#4488ff")}>BLOCH MAP</div>
                <div style={{ fontFamily: "monospace", fontSize: "11px", color: "#ccdae8" }}>{ch.formula}</div>
                {ch.geometry && <div style={{ marginTop: "4px", fontSize: "10.5px" }}>{ch.geometry}</div>}
              </div>
              {ch.insight && (
                <div style={{ ...cS("rgba(255,153,51)"), background: "rgba(255,153,51,0.05)" }}>
                  <div style={cT("#ff9933")}>{"\u21B3"} SQM</div>
                  <span style={{ color: "#d4b896" }}>{ch.insight}</span>
                </div>
              )}
            </>
          )}

          {/* PTM TAB */}
          {tab === "ptm" && ch && (
            <>
              <div style={LS}>PAULI TRANSFER MATRIX</div>
              <div style={{
                background: "rgba(12,14,24,0.8)", borderRadius: "8px", padding: "10px", border: bdr,
              }}>
                <PTMHeatmap runtimeCh={runtimeCh} channel={channel} strength={strength} />
              </div>
              <div style={cS("rgba(255,153,51)")}>
                <div style={cT("#ff9933")}>READING THE PTM</div>
                Diagonal = Pauli component scaling. First row = [1,0,0,0] always (TP). Off-diagonal = mixing.
                {stateCfg.uniform && (
                  <span style={{ color: "#ff6666" }}>
                    {" "}This state is Z-uniform, so Z-row entries don't produce measurable signal.
                  </span>
                )}
              </div>
            </>
          )}

          {/* 2-QUBIT TAB: Correlator bars per topology */}
          {tab === "multi" && (
            <>
              <div style={LS}>CORRELATOR DEFORMATION</div>
              {Object.entries(config.topologies).map(([k, topo]) => (
                (activeTopo === "all" || activeTopo === k) && (
                  <div key={k}>
                    <div style={{ fontSize: "10px", color: "#8899aa", marginBottom: "4px", fontWeight: 500 }}>
                      {topo.name}
                    </div>
                    <CorrelatorBars stateCfg={stateCfg} topo={topo} strength={strength} />
                  </div>
                )
              ))}
              <div style={cS("rgba(204,68,255)")}>
                <div style={cT("#cc44ff")}>STATE x TOPOLOGY</div>
                Switch probe states above — watch how GHZ shows strong {"\u0394\u27E8ZZ\u27E9"} while Cluster shows nearly zero.
                Same noise, different probe = different fingerprint. This is your Finding 1.
              </div>
            </>
          )}

          {/* DATA TAB: Fingerprints */}
          {tab === "data" && (
            <>
              <div style={LS}>EXPERIMENTAL FINGERPRINTS</div>
              <FingerprintViewer data={config.experimentalData} />
              <div style={{ ...cS("rgba(68,255,136)"), background: "rgba(68,255,136,0.04)" }}>
                <div style={cT("#44ff88")}>ADD DATA</div>
                <div style={{ fontSize: "10px" }}>Config {"\u2192"} Exp. Data. Format:</div>
                <pre style={{
                  fontSize: "9.5px", fontFamily: "monospace", color: "#8899bb",
                  marginTop: "4px", whiteSpace: "pre-wrap",
                }}>
{`[{ "label": "GHZ chain p=0.01",
   "noiseStrength": 0.01,
   "topology": "chain",
   "fingerprint": [15 floats] }]`}
                </pre>
              </div>
            </>
          )}
        </div>
      </div>

      {/* CONFIG MODAL */}
      {showConfig && (
        <ConfigEditor
          config={config}
          onUpdate={(c) => { setConfig(c); setShowConfig(false); }}
          onClose={() => setShowConfig(false)}
        />
      )}
    </div>
  );
}
