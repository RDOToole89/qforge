'use dom';

import type { BlochVisualizerData, StoredResultEntry } from "../../../lib/types";
import { LS, bdr, cS, cT } from "../styles";

interface ExperimentSidebarProps {
  storedResults: StoredResultEntry[];
  selectedResult: string | null;
  setSelectedResult: (v: string | null) => void;
  sweepStateType: string;
  setSweepStateType: (v: string) => void;
  sweepQubits: number;
  setSweepQubits: (v: number) => void;
  sweepNoiseType: string;
  setSweepNoiseType: (v: string) => void;
  sweepLoading: boolean;
  launchSweep: () => void;
  hasSweep: boolean;
  activeBloch: BlochVisualizerData | null;
  sweepProgress: number;
  setSweepProgress: (v: number) => void;
  sweepAnimating: boolean;
  setSweepAnimating: (v: boolean) => void;
  sweepAnimRef: React.RefObject<number>;
  toggleSweepAnim: () => void;
  expLoading: boolean;
  expError: string | null;
  tab: "single" | "multi" | "ptm" | "data";
  selectedQubit: number | "all";
  setSelectedQubit: (v: number | "all") => void;
  selectedPair: [number, number];
  setSelectedPair: (v: [number, number]) => void;
  expQubitPairs: [number, number][];
}

export default function ExperimentSidebar(props: ExperimentSidebarProps) {
  const {
    storedResults, selectedResult, setSelectedResult,
    sweepStateType, setSweepStateType, sweepQubits, setSweepQubits,
    sweepNoiseType, setSweepNoiseType, sweepLoading, launchSweep,
    hasSweep, activeBloch, sweepProgress, setSweepProgress,
    sweepAnimating, setSweepAnimating, sweepAnimRef, toggleSweepAnim,
    expLoading, expError, tab, selectedQubit, setSelectedQubit,
    selectedPair, setSelectedPair, expQubitPairs,
  } = props;

  return (
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
              {(activeBloch?.error_rate ?? sweepProgress * 0.5).toFixed(3)}
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

      {activeBloch && (
        <>
          {/* Experiment metadata */}
          <div style={cS("rgba(68,200,255)")}>
            <div style={cT("#44c8ff")}>EXPERIMENT</div>
            <div style={{ fontSize: "10.5px", color: "#a0b0c0" }}>
              <div>{activeBloch.state_type} — {activeBloch.num_qubits} qubits</div>
              {activeBloch.noise_type && (
                <div>Noise: {activeBloch.noise_type} ({activeBloch.error_rate})</div>
              )}
              {activeBloch.fidelity != null && (
                <div>Fidelity: {activeBloch.fidelity.toFixed(4)}</div>
              )}
              <div style={{ fontSize: "9px", color: "#667788", marginTop: "2px" }}>
                Source: {activeBloch.source_mode}
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
                {Array.from({ length: activeBloch.num_qubits }, (_, i) => (
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
  );
}
