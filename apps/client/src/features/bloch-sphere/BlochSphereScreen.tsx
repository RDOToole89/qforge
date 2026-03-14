'use dom';

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { DEFAULT_CONFIG } from "./config";
import { buildRuntime, TAU } from "./math";
import type { BlochConfig } from "./types";
import type { BlochVisualizerData, BlochSweepResponse, StoredResultEntry } from "../../lib/types";
import { listResults, getBlochData, runBlochSweep } from "../../lib/api";
import {
  blochDataToStateCfg,
  blochDataToAllQubits,
  blochDataToPairCfg,
  blochDataToFingerprints,
  getQubitPairs,
} from "./experimentAdapter";
import BlochScene from "./components/BlochScene";
import TwoQubitScene from "./components/TwoQubitScene";
import PTMHeatmap from "./components/PTMHeatmap";
import CorrelatorBars from "./components/CorrelatorBars";
import FingerprintViewer from "./components/FingerprintViewer";
import ConfigEditor from "./components/ConfigEditor";
import ReducedStateExplainer from "./components/ReducedStateExplainer";

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
  // ── Built-in mode state ──
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

  // ── Experiment mode state ──
  const [mode, setMode] = useState<"builtin" | "experiment">("builtin");
  const [storedResults, setStoredResults] = useState<StoredResultEntry[]>([]);
  const [selectedResult, setSelectedResult] = useState<string | null>(null);
  const [blochData, setBlochData] = useState<BlochVisualizerData | null>(null);
  const [expLoading, setExpLoading] = useState(false);
  const [expError, setExpError] = useState<string | null>(null);
  const [selectedQubit, setSelectedQubit] = useState<number | "all">(0);
  const [selectedPair, setSelectedPair] = useState<[number, number]>([0, 1]);

  // ── Sweep mode state ──
  const [sweepData, setSweepData] = useState<BlochSweepResponse | null>(null);
  const [sweepLoading, setSweepLoading] = useState(false);
  const [sweepProgress, setSweepProgress] = useState(0); // 0..1 position in sweep
  const [sweepAnimating, setSweepAnimating] = useState(false);
  const sweepAnimRef = useRef<number>(0);
  // Sweep config form
  const [sweepStateType, setSweepStateType] = useState("GHZ");
  const [sweepQubits, setSweepQubits] = useState(3);
  const [sweepNoiseType, setSweepNoiseType] = useState("depolarizing");
  const [sweepSteps, setSweepSteps] = useState(8);

  const isExp = mode === "experiment";
  const hasSweep = isExp && sweepData !== null && sweepData.snapshots.length > 1;

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

  // Fetch stored results when switching to experiment mode
  useEffect(() => {
    if (mode === "experiment" && storedResults.length === 0) {
      listResults(100, 0)
        .then(setStoredResults)
        .catch(() => setStoredResults([]));
    }
  }, [mode]);

  // Fetch Bloch data when a result is selected
  useEffect(() => {
    if (!selectedResult) { setBlochData(null); return; }
    setExpLoading(true);
    setExpError(null);
    setSweepData(null); // clear sweep when selecting a single result
    setSweepAnimating(false);
    getBlochData(selectedResult)
      .then((data) => {
        setBlochData(data);
        setSelectedQubit(0);
        if (data.num_qubits >= 2) setSelectedPair([0, 1]);
      })
      .catch((e) => setExpError(e.message))
      .finally(() => setExpLoading(false));
  }, [selectedResult]);

  // Sweep: interpolate between snapshots based on sweepProgress (0..1)
  const sweepSnapshot = useMemo((): BlochVisualizerData | null => {
    if (!sweepData || sweepData.snapshots.length === 0) return null;
    const snaps = sweepData.snapshots;
    if (snaps.length === 1) return snaps[0];

    // Map progress to snapshot index (fractional)
    const fIdx = sweepProgress * (snaps.length - 1);
    const lo = Math.floor(fIdx);
    const hi = Math.min(lo + 1, snaps.length - 1);
    const t = fIdx - lo; // interpolation factor 0..1

    if (lo === hi) return snaps[lo];
    const a = snaps[lo];
    const b = snaps[hi];

    // Lerp helper
    const lerp = (x: number, y: number) => x + (y - x) * t;

    // Interpolate qubits
    const qubits = a.qubits.map((qa, i) => {
      const qb = b.qubits[i];
      return {
        qubit_index: qa.qubit_index,
        bloch_vector: {
          rx: lerp(qa.bloch_vector.rx, qb.bloch_vector.rx),
          ry: lerp(qa.bloch_vector.ry, qb.bloch_vector.ry),
          rz: lerp(qa.bloch_vector.rz, qb.bloch_vector.rz),
        },
        purity: lerp(qa.purity, qb.purity),
      };
    });

    // Interpolate pairs
    const pairs = a.pairs.map((pa, i) => {
      const pb = b.pairs[i];
      return {
        qubit_i: pa.qubit_i,
        qubit_j: pa.qubit_j,
        correlators: {
          zi: lerp(pa.correlators.zi, pb.correlators.zi),
          iz: lerp(pa.correlators.iz, pb.correlators.iz),
          zz: lerp(pa.correlators.zz, pb.correlators.zz),
          xx: lerp(pa.correlators.xx, pb.correlators.xx),
          yy: lerp(pa.correlators.yy, pb.correlators.yy),
        },
        mutual_information: lerp(pa.mutual_information, pb.mutual_information),
      };
    });

    // Interpolate MI matrix
    const mi_matrix = a.mi_matrix.map((row, i) =>
      row.map((v, j) => lerp(v, b.mi_matrix[i][j]))
    );

    return {
      ...a,
      error_rate: lerp(a.error_rate ?? 0, b.error_rate ?? 0),
      fidelity: a.fidelity != null && b.fidelity != null
        ? lerp(a.fidelity, b.fidelity) : null,
      qubits,
      pairs,
      mi_matrix,
    };
  }, [sweepData, sweepProgress]);

  // Active Bloch data: sweep-interpolated snapshot or single result
  const _activeBloch = (sweepData && sweepData.snapshots.length > 1) ? sweepSnapshot : blochData;

  // Experiment-mode derived data
  const expStateCfg = useMemo(() => {
    if (!_activeBloch) return null;
    if (selectedQubit === "all") return blochDataToStateCfg(_activeBloch, 0);
    return blochDataToStateCfg(_activeBloch, selectedQubit);
  }, [_activeBloch, selectedQubit]);

  const expAllQubits = useMemo(() => {
    if (!_activeBloch || selectedQubit !== "all") return undefined;
    return blochDataToAllQubits(_activeBloch);
  }, [_activeBloch, selectedQubit]);

  const expPairData = useMemo(() => {
    if (!_activeBloch) return null;
    return blochDataToPairCfg(_activeBloch, selectedPair[0], selectedPair[1]);
  }, [_activeBloch, selectedPair]);

  const expFingerprints = useMemo(() => {
    if (!_activeBloch) return [];
    return blochDataToFingerprints(_activeBloch);
  }, [_activeBloch]);

  const expQubitPairs = useMemo(() => {
    if (!_activeBloch) return [];
    return getQubitPairs(_activeBloch);
  }, [_activeBloch]);

  // The active state config depends on mode
  const activeStateCfg = isExp && expStateCfg ? expStateCfg : stateCfg;

  // Sweep animation
  const toggleSweepAnim = useCallback(() => {
    if (sweepAnimating) {
      setSweepAnimating(false);
      cancelAnimationFrame(sweepAnimRef.current);
      return;
    }
    setSweepAnimating(true);
    let t = sweepProgress;
    const step = () => {
      t += 0.003;
      if (t > 1) t = 0;
      setSweepProgress(t);
      sweepAnimRef.current = requestAnimationFrame(step);
    };
    sweepAnimRef.current = requestAnimationFrame(step);
  }, [sweepAnimating, sweepProgress]);
  useEffect(() => () => cancelAnimationFrame(sweepAnimRef.current), []);

  // Launch a sweep
  const launchSweep = useCallback(() => {
    setSweepLoading(true);
    setExpError(null);
    // Generate error rates from 0 to 0.5
    const rates = Array.from({ length: sweepSteps }, (_, i) =>
      parseFloat((i / (sweepSteps - 1) * 0.5).toFixed(4))
    );
    runBlochSweep({
      state_type: sweepStateType,
      num_qubits: sweepQubits,
      noise_type: sweepNoiseType,
      error_rates: rates,
      sim_mode: "density_matrix",
      shots: 4096,
      rng_seed: 42,
    })
      .then((data) => {
        setSweepData(data);
        setSweepProgress(0);
        setSelectedResult(null); // clear single-result selection
        setBlochData(null);
        setSelectedQubit("all");
      })
      .catch((e) => setExpError(e.message))
      .finally(() => setSweepLoading(false));
  }, [sweepStateType, sweepQubits, sweepNoiseType, sweepSteps]);

  // Built-in mode animation
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
              {m.id === "experiment" && storedResults.length > 0 && (
                <span style={{
                  marginLeft: "4px", fontSize: "9px", padding: "1px 4px",
                  borderRadius: "3px", background: "rgba(68,200,255,0.15)", color: "#44c8ff",
                }}>{storedResults.length}</span>
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
          <button onClick={() => setShowConfig(true)} style={{
            padding: "5px 11px", borderRadius: "6px",
            border: "1px solid rgba(255,153,51,0.25)",
            background: "rgba(255,153,51,0.08)", color: "#ff9933",
            fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
          }}>Config</button>
        )}
      </div>

      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        {/* ── LEFT SIDEBAR ── */}
        <div style={{
          width: "250px", flexShrink: 0, padding: "12px 14px", borderRight: bdr,
          display: "flex", flexDirection: "column", gap: "10px", overflowY: "auto",
        }}>

          {isExp ? (
            /* ── EXPERIMENT MODE LEFT SIDEBAR ── */
            <>
              {/* Result picker */}
              <div>
                <div style={LS}>EXPERIMENT RESULT</div>
                <select
                  value={selectedResult ?? ""}
                  onChange={(e) => setSelectedResult(e.target.value || null)}
                  style={{
                    width: "100%", padding: "5px 8px", borderRadius: "5px",
                    background: "rgba(255,255,255,0.04)", border: bdr,
                    color: "#c8d4e4", fontSize: "10.5px", fontFamily: "inherit",
                  }}
                >
                  <option value="">Select a result...</option>
                  {storedResults.filter(r => !r.error).map((r) => (
                    <option key={r.filename} value={r.filename}>
                      {r.state_type ?? "?"} {r.num_qubits ?? "?"}q — {r.filename.split("/").pop()?.replace("analysis.json", "").replace(/_/g, " ").trim() || r.filename}
                    </option>
                  ))}
                </select>
              </div>

              {/* Sweep controls */}
              <div style={{ borderTop: bdr, paddingTop: "10px" }}>
                <div style={LS}>DECOHERENCE SWEEP</div>
                <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                  <select value={sweepStateType} onChange={(e) => setSweepStateType(e.target.value)} style={{
                    width: "100%", padding: "4px 6px", borderRadius: "4px",
                    background: "rgba(255,255,255,0.04)", border: bdr,
                    color: "#c8d4e4", fontSize: "10px", fontFamily: "inherit",
                  }}>
                    {["GHZ", "W", "BELL", "CLUSTER", "SUPERPOSITION"].map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                  <div style={{ display: "flex", gap: "4px" }}>
                    <select value={sweepQubits} onChange={(e) => setSweepQubits(Number(e.target.value))} style={{
                      flex: 1, padding: "4px 6px", borderRadius: "4px",
                      background: "rgba(255,255,255,0.04)", border: bdr,
                      color: "#c8d4e4", fontSize: "10px", fontFamily: "inherit",
                    }}>
                      {[2,3,4,5,6].map(n => (
                        <option key={n} value={n}>{n}q</option>
                      ))}
                    </select>
                    <select value={sweepNoiseType} onChange={(e) => setSweepNoiseType(e.target.value)} style={{
                      flex: 2, padding: "4px 6px", borderRadius: "4px",
                      background: "rgba(255,255,255,0.04)", border: bdr,
                      color: "#c8d4e4", fontSize: "10px", fontFamily: "inherit",
                    }}>
                      {["depolarizing", "amplitude_damping", "phase_damping", "bit_flip", "phase_flip"].map(n => (
                        <option key={n} value={n}>{n.replace(/_/g, " ")}</option>
                      ))}
                    </select>
                  </div>
                  <button
                    onClick={launchSweep}
                    disabled={sweepLoading}
                    style={{
                      padding: "6px 12px", borderRadius: "5px",
                      fontSize: "11px", fontFamily: "inherit", cursor: sweepLoading ? "wait" : "pointer",
                      background: "rgba(68,200,255,0.12)", border: "1px solid rgba(68,200,255,0.3)",
                      color: "#44c8ff", fontWeight: 600,
                    }}
                  >
                    {sweepLoading ? "Running sweep..." : "Run Sweep (0 \u2192 0.5)"}
                  </button>
                </div>
              </div>

              {/* Sweep playback controls */}
              {hasSweep && (
                <div>
                  <div style={LS}>
                    ERROR RATE — <span style={{ color: "#44c8ff" }}>
                      {(_activeBloch?.error_rate ?? sweepProgress * 0.5).toFixed(3)}
                    </span>
                  </div>
                  <input
                    type="range" min="0" max="1" step="0.002"
                    value={sweepProgress}
                    onChange={(e) => {
                      if (sweepAnimating) { setSweepAnimating(false); cancelAnimationFrame(sweepAnimRef.current); }
                      setSweepProgress(parseFloat(e.target.value));
                    }}
                    style={{ width: "100%", accentColor: "#44c8ff" }}
                  />
                  <button onClick={toggleSweepAnim} style={{
                    width: "100%", padding: "5px 12px", borderRadius: "5px",
                    fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
                    background: sweepAnimating ? "rgba(68,200,255,0.2)" : "rgba(255,255,255,0.04)",
                    border: sweepAnimating ? "1px solid rgba(68,200,255,0.4)" : bdr,
                    color: sweepAnimating ? "#44c8ff" : "#667788",
                    marginTop: "4px",
                  }}>
                    {sweepAnimating ? "\u23F8 Pause" : "\u25B6 Animate Decoherence"}
                  </button>
                </div>
              )}

              {(expLoading || sweepLoading) && (
                <div style={{ fontSize: "11px", color: "#5a6a82", padding: "8px" }}>
                  {sweepLoading ? "Running sweep..." : "Loading Bloch data..."}
                </div>
              )}
              {expError && (
                <div style={{ fontSize: "11px", color: "#ff4466", padding: "8px" }}>
                  {expError}
                </div>
              )}

              {_activeBloch && (
                <>
                  {/* Experiment metadata */}
                  <div style={cS("rgba(68,200,255)")}>
                    <div style={cT("#44c8ff")}>EXPERIMENT</div>
                    <div style={{ fontSize: "10.5px", color: "#a0b0c0" }}>
                      <div>{_activeBloch.state_type} — {_activeBloch.num_qubits} qubits</div>
                      {_activeBloch.noise_type && (
                        <div>Noise: {_activeBloch.noise_type} ({_activeBloch.error_rate})</div>
                      )}
                      {_activeBloch.fidelity != null && (
                        <div>Fidelity: {_activeBloch.fidelity.toFixed(4)}</div>
                      )}
                      <div style={{ fontSize: "9px", color: "#667788", marginTop: "2px" }}>
                        Source: {_activeBloch.source_mode}
                      </div>
                    </div>
                  </div>

                  {/* Qubit selector (1-Qubit tab) */}
                  {tab === "single" && (
                    <div>
                      <div style={LS}>QUBIT</div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "3px" }}>
                        <button
                          onClick={() => setSelectedQubit("all")}
                          style={{
                            padding: "4px 10px", borderRadius: "5px",
                            fontSize: "10px", fontFamily: "inherit", cursor: "pointer",
                            background: selectedQubit === "all" ? "rgba(68,200,255,0.15)" : "rgba(255,255,255,0.02)",
                            border: selectedQubit === "all" ? "1px solid rgba(68,200,255,0.3)" : bdr,
                            color: selectedQubit === "all" ? "#44c8ff" : "#667788",
                          }}
                        >All</button>
                        {Array.from({ length: _activeBloch.num_qubits }, (_, i) => (
                          <button
                            key={i}
                            onClick={() => setSelectedQubit(i)}
                            style={{
                              padding: "4px 10px", borderRadius: "5px",
                              fontSize: "10px", fontFamily: "inherit", cursor: "pointer",
                              background: selectedQubit === i ? "rgba(68,200,255,0.15)" : "rgba(255,255,255,0.02)",
                              border: selectedQubit === i ? "1px solid rgba(68,200,255,0.3)" : bdr,
                              color: selectedQubit === i ? "#44c8ff" : "#667788",
                            }}
                          >Q{i}</button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Pair selector (2-Qubit tab) */}
                  {tab === "multi" && expQubitPairs.length > 0 && (
                    <div>
                      <div style={LS}>QUBIT PAIR</div>
                      <select
                        value={`${selectedPair[0]}-${selectedPair[1]}`}
                        onChange={(e) => {
                          const [a, b] = e.target.value.split("-").map(Number);
                          setSelectedPair([a, b]);
                        }}
                        style={{
                          width: "100%", padding: "5px 8px", borderRadius: "5px",
                          background: "rgba(255,255,255,0.04)", border: bdr,
                          color: "#c8d4e4", fontSize: "10.5px", fontFamily: "inherit",
                        }}
                      >
                        {expQubitPairs.map(([a, b]) => (
                          <option key={`${a}-${b}`} value={`${a}-${b}`}>
                            Q{a} — Q{b}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </>
              )}
            </>
          ) : (
            /* ── BUILT-IN MODE LEFT SIDEBAR ── */
            <>
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
                CPTP maps can only shrink or preserve the Bloch ball. Orange {"\u2286"} Blue.
              </div>
            </>
          )}
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
              stateCfg={activeStateCfg}
              viewMode={isExp ? "state" : viewMode}
              experimentMode={isExp}
              additionalStates={isExp ? expAllQubits : undefined}
            />
          )}
          {tab === "multi" && !isExp && (
            <TwoQubitScene
              topoConfigs={config.topologies}
              activeTopo={activeTopo}
              strength={strength}
              rotation={rotation}
              stateCfg={stateCfg}
            />
          )}
          {tab === "multi" && isExp && expPairData && (
            <TwoQubitScene
              topoConfigs={config.topologies}
              activeTopo="all"
              strength={0}
              rotation={rotation}
              stateCfg={expPairData.stateCfg}
            />
          )}

          {/* Axis legend overlay */}
          <div style={{ position: "absolute", top: "10px", right: "14px", fontSize: "10px", color: "#3a4a5a" }}>
            {tab === "multi"
              ? <><span style={{ color: "#ff4466" }}>{"\u2501"}</span> {"\u27E8"}ZI{"\u27E9"} <span style={{ color: "#44ff88" }}>{"\u2501"}</span> {"\u27E8"}IZ{"\u27E9"} <span style={{ color: "#4488ff" }}>{"\u2501"}</span> {"\u27E8"}ZZ{"\u27E9"}</>
              : <><span style={{ color: "#ff4466" }}>{"\u2501"}</span> X <span style={{ color: "#44ff88" }}>{"\u2501"}</span> Y <span style={{ color: "#4488ff" }}>{"\u2501"}</span> Z</>
            }
          </div>

          {/* State name overlay */}
          <div style={{
            position: "absolute", top: "10px", left: "14px",
            fontSize: "11px", color: activeStateCfg.color ?? "#fff", fontWeight: 600,
          }}>
            {activeStateCfg.name}
            {activeStateCfg.uniform && !isExp && (
              <span style={{ fontSize: "9px", opacity: 0.5, fontWeight: 400, marginLeft: "6px" }}>
                uniform Z-dist
              </span>
            )}
            {isExp && _activeBloch?.source_mode === "diagonal_estimate" && (
              <span style={{ fontSize: "9px", color: "#dda030", fontWeight: 400, marginLeft: "6px" }}>
                Z-basis only
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
            ...cS(`${activeStateCfg.color ?? "#ff9933"}`),
            background: `${activeStateCfg.color ?? "#ff9933"}0a`,
            border: `1px solid ${activeStateCfg.color ?? "#ff9933"}20`,
          }}>
            <div style={cT(activeStateCfg.color ?? "#ff9933")}>
              {activeStateCfg.name} — {
                activeStateCfg.zBasisSignal === "strong" ? "Z-BASIS SENSITIVE"
                : activeStateCfg.zBasisSignal === "weak" ? "Z-BASIS WEAK"
                : "Z-BASIS BLIND"
              }
            </div>
            <span style={{ color: "#a0b0c0" }}>{activeStateCfg.insight}</span>
          </div>

          {/* ── EXPERIMENT MODE RIGHT SIDEBAR ── */}
          {isExp && _activeBloch && (() => {
            const ab = _activeBloch; // narrow for TypeScript
            return (
            <>
              {/* 1-Qubit tab: educational panels */}
              {tab === "single" && (
                <>
                  <ReducedStateExplainer
                    context="single"
                    purity={selectedQubit !== "all" ? ab.qubits[selectedQubit]?.purity : undefined}
                    numQubits={ab.num_qubits}
                  />
                  {ab.source_mode === "diagonal_estimate" && (
                    <ReducedStateExplainer context="diagonal_warning" />
                  )}
                  {selectedQubit === "all" && ab.num_qubits > 1 && (
                    <ReducedStateExplainer
                      context="multi_qubit_insight"
                      sourceMode={ab.source_mode}
                    />
                  )}
                </>
              )}

              {/* 2-Qubit tab: correlator bars */}
              {tab === "multi" && expPairData && (
                <>
                  <div style={LS}>MEASURED CORRELATORS</div>
                  <CorrelatorBars
                    stateCfg={expPairData.stateCfg}
                    topo={Object.values(config.topologies)[0]}
                    strength={0}
                    experimentCorrelators={expPairData.correlators as { zi: number; iz: number; zz: number; xx: number; yy: number }}
                  />
                  <div style={cS("rgba(68,200,255)")}>
                    <div style={cT("#44c8ff")}>MUTUAL INFORMATION</div>
                    <span style={{ color: "#a0b0c0", fontFamily: "monospace" }}>
                      I(Q{selectedPair[0]}:Q{selectedPair[1]}) = {expPairData.mutualInfo.toFixed(4)} bits
                    </span>
                  </div>
                  <ReducedStateExplainer context="multi" />
                </>
              )}

              {/* PTM tab: show MI matrix as heatmap */}
              {tab === "ptm" && (
                <>
                  <div style={LS}>MUTUAL INFORMATION MATRIX</div>
                  <div style={{
                    background: "rgba(12,14,24,0.8)", borderRadius: "8px", padding: "10px", border: bdr,
                  }}>
                    <MIMatrixHeatmap matrix={ab.mi_matrix} />
                  </div>
                  <div style={cS("rgba(68,200,255)")}>
                    <div style={cT("#44c8ff")}>READING THE MI MATRIX</div>
                    Mutual information measures total correlations between qubit pairs.
                    Higher values (brighter) indicate stronger quantum or classical correlations.
                  </div>
                </>
              )}

              {/* Data tab: metrics fingerprints */}
              {tab === "data" && (
                <>
                  <div style={LS}>EXPERIMENT METRICS</div>
                  {ab.metrics ? (
                    <>
                      <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                        {Object.entries(ab.metrics).map(([name, entry]) => (
                          <div key={name} style={{
                            display: "flex", alignItems: "center", gap: "6px",
                            fontSize: "10.5px", fontFamily: "monospace",
                          }}>
                            <span style={{ color: "#8899aa", width: "120px", overflow: "hidden", textOverflow: "ellipsis" }}>
                              {name}
                            </span>
                            <span style={{ color: "#c8d4e4" }}>{entry.value.toFixed(4)}</span>
                            {entry.ci95 && (
                              <span style={{ color: "#556677", fontSize: "9px" }}>
                                [{entry.ci95[0].toFixed(3)}, {entry.ci95[1].toFixed(3)}]
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                      <div style={LS}>FINGERPRINT</div>
                      <FingerprintViewer data={expFingerprints} />
                    </>
                  ) : (
                    <div style={{ fontSize: "11px", color: "#4a5a6a", fontStyle: "italic", padding: "10px" }}>
                      No metrics available. Run with enable_research_metrics=True.
                    </div>
                  )}
                </>
              )}
            </>
          );
          })()}

          {/* ── BUILT-IN MODE RIGHT SIDEBAR ── */}
          {!isExp && (
            <>
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

/** Simple MI matrix heatmap for experiment mode PTM tab */
function MIMatrixHeatmap({ matrix }: { matrix: number[][] }) {
  const n = matrix.length;
  const mx = Math.max(...matrix.flat().filter((_, i) => Math.floor(i / n) !== i % n), 0.01);

  return (
    <div>
      <div style={{ display: "flex", marginLeft: "28px" }}>
        {Array.from({ length: n }, (_, i) => (
          <div key={i} style={{
            width: "32px", textAlign: "center", fontSize: "9px",
            color: "#8899aa", fontFamily: "monospace", fontWeight: 600,
          }}>Q{i}</div>
        ))}
      </div>
      {matrix.map((row, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center" }}>
          <div style={{
            width: "28px", fontSize: "9px", textAlign: "right", paddingRight: "5px",
            color: "#8899aa", fontFamily: "monospace", fontWeight: 600,
          }}>Q{i}</div>
          {row.map((v, j) => (
            <div key={j} style={{
              width: "32px", height: "24px", display: "flex", alignItems: "center", justifyContent: "center",
              background: i === j ? "rgba(255,255,255,0.02)"
                : `rgba(68,200,255,${Math.min(v / mx * 0.7, 0.7)})`,
              borderRadius: "3px", margin: "1px",
              fontSize: "8px", fontFamily: "monospace",
              color: i === j ? "#334" : v / mx > 0.4 ? "#fff" : "#556",
            }}>
              {i === j ? "\u2014" : v.toFixed(2)}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
