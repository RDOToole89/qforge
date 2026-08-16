'use dom';

import { chrome, viz } from "@/src/design/tokens";
import type { BlochVisualizerData } from "../../../lib/types";
import type { BlochConfig, ProbeStateConfig, RuntimeChannel, ExperimentalDataEntry, CorrelatorSignature } from "../types";
import { LS, bdr, cS, cT, rgba } from "../styles";
import PTMHeatmap from "./PTMHeatmap";
import CorrelatorBars from "./CorrelatorBars";
import FingerprintViewer from "./FingerprintViewer";
import ReducedStateExplainer from "./ReducedStateExplainer";
import MIMatrixHeatmap from "./MIMatrixHeatmap";

interface DataPanelProps {
  isExp: boolean;
  tab: "single" | "multi" | "ptm" | "data";
  activeStateCfg: ProbeStateConfig;
  // Built-in mode props
  config: BlochConfig;
  ch: RuntimeChannel | undefined;
  runtimeCh: Record<string, RuntimeChannel>;
  channel: string;
  strength: number;
  stateCfg: ProbeStateConfig;
  activeTopo: string;
  // Experiment mode props
  activeBloch: BlochVisualizerData | null;
  selectedQubit: number | "all";
  selectedPair: [number, number];
  expPairData: { stateCfg: ProbeStateConfig; correlators: CorrelatorSignature; mutualInfo: number } | null;
  expFingerprints: ExperimentalDataEntry[];
}

export default function DataPanel(props: DataPanelProps) {
  const {
    isExp, tab, activeStateCfg,
    config, ch, runtimeCh, channel, strength, stateCfg, activeTopo,
    activeBloch, selectedQubit, selectedPair, expPairData, expFingerprints,
  } = props;

  const stateColor = activeStateCfg.color ?? viz.orange;

  return (
    <div style={{
      width: "280px", flexShrink: 0, padding: "12px 14px", borderLeft: bdr,
      overflowY: "auto", display: "flex", flexDirection: "column", gap: "10px",
    }}>

      {/* STATE INFO -- always shown */}
      <div style={{
        ...cS(stateColor),
        background: `${stateColor}0a`,
        border: `1px solid ${stateColor}20`,
      }}>
        <div style={cT(stateColor)}>
          {activeStateCfg.name} — {
            activeStateCfg.zBasisSignal === "strong" ? "Z-BASIS SENSITIVE"
            : activeStateCfg.zBasisSignal === "weak" ? "Z-BASIS WEAK"
            : "Z-BASIS BLIND"
          }
        </div>
        <span style={{ color: chrome.text.secondary }}>{activeStateCfg.insight}</span>
      </div>

      {/* EXPERIMENT MODE RIGHT SIDEBAR */}
      {isExp && activeBloch && (() => {
        const ab = activeBloch; // narrow for TypeScript
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
              <div style={cS(viz.cyan)}>
                <div style={cT(viz.cyan)}>MUTUAL INFORMATION</div>
                <span style={{ color: chrome.text.secondary, fontFamily: "monospace" }}>
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
                background: rgba(chrome.bg.primary, 0.8), borderRadius: "8px", padding: "10px", border: bdr,
              }}>
                <MIMatrixHeatmap matrix={ab.mi_matrix} />
              </div>
              <div style={cS(viz.cyan)}>
                <div style={cT(viz.cyan)}>READING THE MI MATRIX</div>
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
                        <span style={{ color: chrome.text.secondary, width: "120px", overflow: "hidden", textOverflow: "ellipsis" }}>
                          {name}
                        </span>
                        <span style={{ color: chrome.text.primary }}>{entry.value.toFixed(4)}</span>
                        {entry.ci95 && (
                          <span style={{ color: chrome.text.tertiary, fontSize: "9px" }}>
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
                <div style={{ fontSize: "11px", color: chrome.text.tertiary, fontStyle: "italic", padding: "10px" }}>
                  No metrics available. Run with metrics enabled (e.g. metrics="decoherence").
                </div>
              )}
            </>
          )}
        </>
      );
      })()}

      {/* BUILT-IN MODE RIGHT SIDEBAR */}
      {!isExp && (
        <>
          {/* 1-QUBIT TAB: Channel info */}
          {tab === "single" && ch && (
            <>
              <div style={cS(viz.orange)}>
                <div style={cT(viz.orange)}>KRAUS OPERATORS</div>
                <div style={{ fontFamily: "monospace", fontSize: "10px", color: chrome.text.secondary, wordBreak: "break-all" }}>
                  {ch.kraus ?? "—"}
                </div>
              </div>
              <div style={cS(viz.blue)}>
                <div style={cT(viz.blue)}>BLOCH MAP</div>
                <div style={{ fontFamily: "monospace", fontSize: "11px", color: chrome.text.primary }}>{ch.formula}</div>
                {ch.geometry && <div style={{ marginTop: "4px", fontSize: "10.5px" }}>{ch.geometry}</div>}
              </div>
              {ch.insight && (
                <div style={{ ...cS(viz.orange), background: `${viz.orange}0d` }}>
                  <div style={cT(viz.orange)}>{"↳"} INSIGHT</div>
                  <span style={{ color: chrome.text.secondary }}>{ch.insight}</span>
                </div>
              )}
            </>
          )}

          {/* PTM TAB */}
          {tab === "ptm" && ch && (
            <>
              <div style={LS}>PAULI TRANSFER MATRIX</div>
              <div style={{
                background: rgba(chrome.bg.primary, 0.8), borderRadius: "8px", padding: "10px", border: bdr,
              }}>
                <PTMHeatmap runtimeCh={runtimeCh} channel={channel} strength={strength} />
              </div>
              <div style={cS(viz.orange)}>
                <div style={cT(viz.orange)}>READING THE PTM</div>
                Diagonal = Pauli component scaling. First row = [1,0,0,0] always (TP). Off-diagonal = mixing.
                {stateCfg.uniform && (
                  <span style={{ color: chrome.status.error }}>
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
                    <div style={{ fontSize: "10px", color: chrome.text.secondary, marginBottom: "4px", fontWeight: 500 }}>
                      {topo.name}
                    </div>
                    <CorrelatorBars stateCfg={stateCfg} topo={topo} strength={strength} />
                  </div>
                )
              ))}
              <div style={cS(viz.magenta)}>
                <div style={cT(viz.magenta)}>STATE x TOPOLOGY</div>
                Switch probe states above — watch how GHZ shows strong {"Δ⟨ZZ⟩"} while Cluster shows nearly zero.
                Same noise, different probe = different fingerprint. This is your Finding 1.
              </div>
            </>
          )}

          {/* DATA TAB: Fingerprints */}
          {tab === "data" && (
            <>
              <div style={LS}>EXPERIMENTAL FINGERPRINTS</div>
              <FingerprintViewer data={config.experimentalData} />
              <div style={{ ...cS(viz.green), background: `${viz.green}0a` }}>
                <div style={cT(viz.green)}>ADD DATA</div>
                <div style={{ fontSize: "10px" }}>Config {"→"} Exp. Data. Format:</div>
                <pre style={{
                  fontSize: "9.5px", fontFamily: "monospace", color: chrome.text.secondary,
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
  );
}
