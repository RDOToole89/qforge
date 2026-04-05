"use dom";

import { useState, useEffect, useRef, useCallback } from "react";
import UnifiedBlochSphere from "@/src/features/bloch-sphere/components/UnifiedBlochSphere";
import CorrelationHeatmap from "./CorrelationHeatmap";
import type { UsePlaybackReturn } from "../hooks/usePlayback";
import { colors, fonts } from "../styles";

interface BlochPlaybackPanelProps {
  playback: UsePlaybackReturn;
  numQubits: number;
  /** Externally control fullscreen (for onboarding) */
  fullscreenOpen?: boolean;
  onFullscreenChange?: (open: boolean) => void;
  /** When set, shows a preview caption above the sphere */
  previewCaption?: string | null;
  /** Qubits currently being operated on — highlighted on Bloch sphere */
  activeQubits?: number[];
  /** Current gate being applied, e.g. "H(q0)" — shown as "now playing" */
  activeGateLabel?: string | null;
  /** Color of the active gate */
  activeGateColor?: string | null;
}

const SPEED_OPTIONS = [0.25, 0.5, 1, 2, 4];

export default function BlochPlaybackPanel({ playback, numQubits, fullscreenOpen, onFullscreenChange, previewCaption, activeQubits, activeGateLabel, activeGateColor }: BlochPlaybackPanelProps) {
  const [internalFs, setInternalFs] = useState(false);
  // Sync external fullscreen control
  useEffect(() => {
    if (fullscreenOpen !== undefined) setInternalFs(fullscreenOpen);
  }, [fullscreenOpen]);
  const fullscreen = internalFs;
  const setFullscreen = (v: boolean) => { setInternalFs(v); onFullscreenChange?.(v); };
  const [corrMode, setCorrMode] = useState<"correlation" | "concurrence" | "tangle">("correlation");
  const [blochZoom, setBlochZoom] = useState(1.25);
  const { state, play, pause, stepBack, stepForward, setSpeed, reset, seek, scrubTo, snapToStep, totalSnapshots } = playback;
  const { status, snapshotIndex, speed, dots, correlations, progress } = state;

  const hasCircuit = totalSnapshots > 1;

  return (
    <>
      {/* Inline panel */}
      <div style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        background: colors.surface,
        borderLeft: `1px solid ${colors.border}`,
      }}>
        {/* Header */}
        <div style={{
          padding: "10px 14px",
          borderBottom: `1px solid ${colors.border}`,
          fontSize: 12,
          fontWeight: 600,
          color: colors.textSecondary,
          textTransform: "uppercase",
          letterSpacing: "0.5px",
          fontFamily: fonts.sans,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}>
          <span>{previewCaption ? "Gate Preview" : "Bloch Sphere"}</span>
          <button
            data-onboarding="expand-bloch"
            onClick={() => setFullscreen(true)}
            title="Expand to fullscreen"
            style={{
              background: "transparent",
              border: `1px solid ${colors.border}`,
              borderRadius: 4,
              color: colors.textTertiary,
              fontSize: 13,
              cursor: "pointer",
              width: 26,
              height: 26,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: 0,
            }}
          >
            {"\u26F6"}
          </button>
        </div>

        {/* Preview caption */}
        {previewCaption && (
          <div style={{
            padding: "6px 14px",
            fontSize: 11,
            color: colors.accentLight,
            fontFamily: fonts.sans,
            lineHeight: 1.4,
            borderBottom: `1px solid ${colors.border}`,
            background: `${colors.accentDim}40`,
          }}>
            {previewCaption}
          </div>
        )}

        {/* Sphere — fills all available space, double-click to open modal */}
        <div
          onDoubleClick={() => setFullscreen(true)}
          style={{
            flex: 1,
            minHeight: 0,
            width: "100%",
            cursor: "pointer",
            overflow: "hidden",
          }}
          title="Double-click to expand"
        >
          {(hasCircuit || previewCaption) ? (
            <UnifiedBlochSphere mode="circuit" dots={dots} zoom={blochZoom} activeQubits={activeQubits} stepProgress={state.t} />
          ) : (
            <div style={{
              color: colors.textTertiary,
              fontSize: 12,
              fontFamily: fonts.sans,
              textAlign: "center",
              padding: 20,
            }}>
              Add gates to see
              <br />
              Bloch sphere preview
            </div>
          )}
        </div>

        {/* Now playing: current gate */}
        {activeGateLabel && (
          <div style={{
            padding: "4px 14px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 6,
          }}>
            <div style={{
              width: 4,
              height: 4,
              borderRadius: 2,
              background: activeGateColor ?? colors.accent,
              animation: "fadeIn 0.2s ease",
            }} />
            <span style={{
              fontSize: 11,
              fontWeight: 600,
              fontFamily: fonts.mono,
              color: activeGateColor ?? colors.accentLight,
              animation: "fadeIn 0.2s ease",
            }}>
              {activeGateLabel}
            </span>
          </div>
        )}

        {/* Zoom slider */}
        {(hasCircuit || previewCaption) && (
          <div style={{
            padding: "2px 14px",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}>
            <span style={{ fontSize: 9, color: colors.textTertiary, fontFamily: fonts.mono }}>-</span>
            <input
              type="range"
              min={0.5}
              max={2.0}
              step={0.05}
              value={blochZoom}
              onChange={(e) => setBlochZoom(parseFloat(e.target.value))}
              style={{ flex: 1, accentColor: colors.textTertiary, height: 3, cursor: "pointer" }}
            />
            <span style={{ fontSize: 9, color: colors.textTertiary, fontFamily: fonts.mono }}>+</span>
          </div>
        )}

        <QubitLegend dots={dots} hasCircuit={hasCircuit} />

        {/* Live Bloch state readout */}
        {hasCircuit && dots.length > 0 && (
          <div style={{
            padding: "4px 14px 6px",
            borderTop: `1px solid ${colors.border}`,
            display: "flex",
            flexDirection: "column",
            gap: 3,
          }}>
            {dots.map((d, i) => {
              const len = Math.sqrt(d.rx * d.rx + d.ry * d.ry + d.rz * d.rz);
              const purity = len > 0.95 ? "pure" : len < 0.15 ? "mixed" : `${(len * 100).toFixed(0)}%`;
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 9, fontFamily: fonts.mono }}>
                  <div style={{ width: 6, height: 6, borderRadius: 3, background: d.color, flexShrink: 0 }} />
                  <span style={{ color: colors.textTertiary, minWidth: 16 }}>q{i}</span>
                  <span style={{ color: colors.textSecondary }}>
                    ({d.rx >= 0 ? "+" : ""}{d.rx.toFixed(2)},
                    {d.ry >= 0 ? " +" : " "}{d.ry.toFixed(2)},
                    {d.rz >= 0 ? " +" : " "}{d.rz.toFixed(2)})
                  </span>
                  <span style={{ color: len > 0.95 ? colors.success : len < 0.15 ? colors.warning : colors.textTertiary, fontSize: 8 }}>
                    {purity}
                  </span>
                </div>
              );
            })}
          </div>
        )}

        {/* Correlation heatmap */}
        {hasCircuit && correlations && numQubits >= 2 && (
          <div data-onboarding="correlation-panel">
            <CorrelationPanel correlations={correlations} numQubits={numQubits} corrMode={corrMode} setCorrMode={setCorrMode} />
          </div>
        )}

        <TransportControls
          hasCircuit={hasCircuit}
          status={status}
          snapshotIndex={snapshotIndex}
          totalSnapshots={totalSnapshots}
          speed={speed}
          progress={progress}
          play={play}
          pause={pause}
          stepBack={stepBack}
          stepForward={stepForward}
          setSpeed={setSpeed}
          reset={reset}
          onScrub={scrubTo}
          onScrubEnd={snapToStep}
        />
      </div>

      {/* Fullscreen modal */}
      {fullscreen && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            background: "rgba(0, 0, 0, 0.85)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) setFullscreen(false);
          }}
        >
          <div style={{
            background: colors.bg,
            borderRadius: 16,
            border: `1px solid ${colors.border}`,
            width: "min(90vw, 720px)",
            maxHeight: "90vh",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            boxShadow: "0 24px 80px rgba(0,0,0,0.6)",
          }}>
            {/* Modal header */}
            <div style={{
              padding: "14px 20px",
              borderBottom: `1px solid ${colors.border}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}>
              <span style={{
                fontSize: 16,
                fontWeight: 700,
                color: colors.text,
                fontFamily: fonts.sans,
              }}>
                Bloch Sphere
              </span>
              <button
                onClick={() => setFullscreen(false)}
                style={{
                  background: "transparent",
                  border: `1px solid ${colors.border}`,
                  borderRadius: 6,
                  color: colors.textSecondary,
                  fontSize: 14,
                  cursor: "pointer",
                  width: 32,
                  height: 32,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: 0,
                  fontFamily: fonts.sans,
                }}
                title="Close"
              >
                {"\u2715"}
              </button>
            </div>

            {/* Large sphere */}
            <div data-onboarding="modal-sphere" style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: 24,
              minHeight: 400,
            }}>
              {hasCircuit ? (
                <UnifiedBlochSphere mode="circuit" dots={dots} size={520} zoom={blochZoom} activeQubits={activeQubits} stepProgress={state.t} />
              ) : (
                <div style={{
                  color: colors.textTertiary,
                  fontSize: 14,
                  fontFamily: fonts.sans,
                  textAlign: "center",
                }}>
                  Add gates to see the Bloch sphere
                </div>
              )}
            </div>

            {/* Now playing in modal */}
            {activeGateLabel && (
              <div style={{
                padding: "4px 20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 8,
              }}>
                <div style={{
                  width: 6, height: 6, borderRadius: 3,
                  background: activeGateColor ?? colors.accent,
                }} />
                <span style={{
                  fontSize: 13,
                  fontWeight: 600,
                  fontFamily: fonts.mono,
                  color: activeGateColor ?? colors.accentLight,
                }}>
                  {activeGateLabel}
                </span>
              </div>
            )}

            {/* Zoom slider in modal */}
            {hasCircuit && (
              <div style={{ padding: "2px 40px", display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ fontSize: 9, color: colors.textTertiary, fontFamily: fonts.mono }}>-</span>
                <input
                  type="range"
                  min={0.5}
                  max={2.0}
                  step={0.05}
                  value={blochZoom}
                  onChange={(e) => setBlochZoom(parseFloat(e.target.value))}
                  style={{ flex: 1, accentColor: colors.textTertiary, height: 3, cursor: "pointer" }}
                />
                <span style={{ fontSize: 9, color: colors.textTertiary, fontFamily: fonts.mono }}>+</span>
              </div>
            )}

            {/* Controls */}
            <div style={{ padding: "0 20px" }}>
              <QubitLegend dots={dots} hasCircuit={hasCircuit} />
            </div>

            {/* Live state readout in modal */}
            {hasCircuit && dots.length > 0 && (
              <div style={{ padding: "4px 34px 6px", display: "flex", flexWrap: "wrap", gap: "2px 16px", justifyContent: "center" }}>
                {dots.map((d, i) => {
                  const len = Math.sqrt(d.rx * d.rx + d.ry * d.ry + d.rz * d.rz);
                  const purity = len > 0.95 ? "pure" : len < 0.15 ? "mixed" : `${(len * 100).toFixed(0)}%`;
                  return (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10, fontFamily: fonts.mono }}>
                      <div style={{ width: 6, height: 6, borderRadius: 3, background: d.color, flexShrink: 0 }} />
                      <span style={{ color: colors.textTertiary }}>q{i}</span>
                      <span style={{ color: colors.textSecondary }}>
                        ({d.rx >= 0 ? "+" : ""}{d.rx.toFixed(2)},
                        {d.ry >= 0 ? " +" : " "}{d.ry.toFixed(2)},
                        {d.rz >= 0 ? " +" : " "}{d.rz.toFixed(2)})
                      </span>
                      <span style={{ color: len > 0.95 ? colors.success : len < 0.15 ? colors.warning : colors.textTertiary, fontSize: 9 }}>
                        {purity}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}

            {hasCircuit && correlations && numQubits >= 2 && (
              <div data-onboarding="modal-correlation" style={{ padding: "0 20px", display: "flex", justifyContent: "center" }}>
                <CorrelationPanel correlations={correlations} numQubits={numQubits} corrMode={corrMode} setCorrMode={setCorrMode} />
              </div>
            )}
            <div data-onboarding="modal-controls" style={{ padding: "0 20px 16px" }}>
              <TransportControls
                hasCircuit={hasCircuit}
                status={status}
                snapshotIndex={snapshotIndex}
                totalSnapshots={totalSnapshots}
                speed={speed}
                progress={progress}
                play={play}
                pause={pause}
                stepBack={stepBack}
                stepForward={stepForward}
                setSpeed={setSpeed}
                reset={reset}
                onScrub={scrubTo}
                onScrubEnd={snapToStep}
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// ── Shared sub-components ───────────────────────────────────────

function QubitLegend({ dots, hasCircuit }: { dots: { color: string }[]; hasCircuit: boolean }) {
  if (!hasCircuit) return null;
  return (
    <div style={{
      padding: "6px 14px",
      display: "flex",
      flexWrap: "wrap",
      gap: 8,
      borderTop: `1px solid ${colors.border}`,
    }}>
      {dots.map((d, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <div style={{ width: 8, height: 8, borderRadius: 4, background: d.color }} />
          <span style={{ fontSize: 10, color: colors.textSecondary, fontFamily: fonts.mono }}>
            q{i}
          </span>
        </div>
      ))}
    </div>
  );
}

interface TransportControlsProps {
  hasCircuit: boolean;
  status: string;
  snapshotIndex: number;
  totalSnapshots: number;
  speed: number;
  progress: number;
  play: () => void;
  pause: () => void;
  stepBack: () => void;
  stepForward: () => void;
  setSpeed: (s: number) => void;
  reset: () => void;
  onScrub?: (progress: number) => void;
  onScrubEnd?: () => void;
}

function TransportControls({
  hasCircuit, status, snapshotIndex, totalSnapshots,
  speed, progress, play, pause, stepBack, stepForward, setSpeed, reset, onScrub, onScrubEnd,
}: TransportControlsProps) {
  const scrubberRef = useRef<HTMLDivElement>(null);
  const isDraggingRef = useRef(false);

  const handleScrubFromEvent = useCallback((clientX: number) => {
    const el = scrubberRef.current;
    if (!el || !onScrub) return;
    const rect = el.getBoundingClientRect();
    const p = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    onScrub(p);
  }, [onScrub]);

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    isDraggingRef.current = true;
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
    handleScrubFromEvent(e.clientX);
  }, [handleScrubFromEvent]);

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    if (!isDraggingRef.current) return;
    handleScrubFromEvent(e.clientX);
  }, [handleScrubFromEvent]);

  const handlePointerUp = useCallback(() => {
    isDraggingRef.current = false;
    onScrubEnd?.();
  }, [onScrubEnd]);

  // Step tick marks as fractions
  const stepTicks = totalSnapshots > 1
    ? Array.from({ length: totalSnapshots }, (_, i) => i / (totalSnapshots - 1))
    : [];

  return (
    <div style={{
      padding: "8px 14px",
      borderTop: `1px solid ${colors.border}`,
      display: "flex",
      flexDirection: "column",
      gap: 6,
    }}>
      {/* Continuous timeline scrubber */}
      {hasCircuit && totalSnapshots > 1 && (
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 9, color: colors.textTertiary, fontFamily: fonts.mono, minWidth: 8 }}>0</span>
          <div
            ref={scrubberRef}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={handlePointerUp}
            style={{
              flex: 1,
              height: 20,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              position: "relative",
              touchAction: "none",
            }}
          >
            {/* Track background */}
            <div style={{
              position: "absolute",
              left: 0, right: 0, top: 8,
              height: 4,
              borderRadius: 2,
              background: colors.border,
            }} />
            {/* Filled track */}
            <div style={{
              position: "absolute",
              left: 0, top: 8,
              width: `${progress * 100}%`,
              height: 4,
              borderRadius: 2,
              background: colors.accent,
            }} />
            {/* Step tick marks */}
            {stepTicks.map((tick, i) => (
              <div key={i} style={{
                position: "absolute",
                left: `${tick * 100}%`,
                top: 5,
                width: 2,
                height: 10,
                borderRadius: 1,
                background: i <= snapshotIndex ? colors.accentLight : colors.textTertiary,
                opacity: 0.5,
                transform: "translateX(-1px)",
              }} />
            ))}
            {/* Thumb */}
            <div style={{
              position: "absolute",
              left: `${progress * 100}%`,
              top: 4,
              width: 12,
              height: 12,
              borderRadius: 6,
              background: colors.accent,
              border: "2px solid #fff",
              transform: "translateX(-6px)",
              boxShadow: "0 1px 4px rgba(0,0,0,0.3)",
            }} />
          </div>
          <span style={{ fontSize: 9, color: colors.textTertiary, fontFamily: fonts.mono, minWidth: 8 }}>
            {totalSnapshots - 1}
          </span>
        </div>
      )}

      {/* Moment indicator */}
      <div style={{
        fontSize: 11,
        color: colors.textTertiary,
        fontFamily: fonts.mono,
        textAlign: "center",
      }}>
        {hasCircuit ? `Step ${snapshotIndex} / ${totalSnapshots - 1}` : "No circuit"}
      </div>

      {/* Buttons row */}
      <div style={{ display: "flex", gap: 4, justifyContent: "center" }}>
        <TransportButton onClick={reset} disabled={!hasCircuit} title="Reset">
          {"\u23EE"}
        </TransportButton>
        <TransportButton onClick={stepBack} disabled={!hasCircuit || snapshotIndex === 0} title="Step back">
          {"\u23EA"}
        </TransportButton>
        {status === "playing" ? (
          <TransportButton onClick={pause} disabled={!hasCircuit} title="Pause" accent>
            {"\u23F8"}
          </TransportButton>
        ) : (
          <TransportButton onClick={play} disabled={!hasCircuit} title="Play" accent>
            {"\u25B6"}
          </TransportButton>
        )}
        <TransportButton onClick={stepForward} disabled={!hasCircuit || snapshotIndex >= totalSnapshots - 1} title="Step forward">
          {"\u23E9"}
        </TransportButton>
      </div>

      {/* Speed selector */}
      <div style={{ display: "flex", gap: 2, justifyContent: "center" }}>
        {SPEED_OPTIONS.map((s) => (
          <button
            key={s}
            onClick={() => setSpeed(s)}
            style={{
              background: speed === s ? colors.accentDim : "transparent",
              color: speed === s ? colors.accentLight : colors.textTertiary,
              border: `1px solid ${speed === s ? colors.accent : "transparent"}`,
              borderRadius: 4,
              padding: "2px 6px",
              fontSize: 10,
              fontFamily: fonts.mono,
              cursor: "pointer",
            }}
          >
            {s}x
          </button>
        ))}
      </div>
    </div>
  );
}

type CorrMode = "correlation" | "concurrence" | "tangle";

const CORR_INFO: Record<CorrMode, { title: string; explanation: string; formula: string; example: string }> = {
  correlation: {
    title: "\u0394Cov \u2014 Connected Correlation",
    explanation: "Measures how much two qubits' measurement outcomes are correlated beyond what you'd expect from their individual states. If measuring one qubit tells you something about the other, this value is nonzero.",
    formula: "\u0394Cov(i,j) = \u27E8Z\u1D62Z\u2C6C\u27E9 \u2212 \u27E8Z\u1D62\u27E9\u27E8Z\u2C6C\u27E9",
    example: "A Bell state (|00\u27E9+|11\u27E9)/\u221A2 has \u0394Cov = +1.0: measuring q0 as |0\u27E9 guarantees q1 is also |0\u27E9. A product state like |+\u27E9|0\u27E9 has \u0394Cov = 0: the qubits are independent.",
  },
  concurrence: {
    title: "Concurrence \u2014 Pairwise Entanglement",
    explanation: "Quantifies genuine quantum entanglement between two qubits. Unlike correlation, concurrence is zero for classically correlated states \u2014 it only detects entanglement that has no classical explanation.",
    formula: "C = max(0, \u221A\u03BB\u2081 \u2212 \u221A\u03BB\u2082 \u2212 \u221A\u03BB\u2083 \u2212 \u221A\u03BB\u2084)  (Wootters)",
    example: "C = 0 means separable (no entanglement). C = 1 means maximally entangled (Bell state). A GHZ state has C = 0 for all pairs \u2014 the entanglement is genuinely 3-way, not pairwise.",
  },
  tangle: {
    title: "Tangle \u2014 Multipartite Entanglement",
    explanation: "Measures genuinely multipartite entanglement \u2014 the part that can't be explained by any combination of pairwise entanglement. Uses the Coffman-Kundu-Wootters (CKW) residual tangle for 3 qubits, generalized for larger systems.",
    formula: "\u03C4\u2083 = C\u00B2(A|BC) \u2212 C\u00B2(A,B) \u2212 C\u00B2(A,C)",
    example: "GHZ state: \u03C4 = 1.0 (maximal), all pairwise C = 0. The entanglement is entirely tripartite \u2014 you can't split it into pairs. W state: \u03C4 = 0, pairwise C = 2/3. All entanglement is in pairs \u2014 no genuinely 3-way part.",
  },
};

function CorrelationPanel({
  correlations, numQubits, corrMode, setCorrMode,
}: {
  correlations: import("../hooks/usePlayback").CorrelationData;
  numQubits: number;
  corrMode: CorrMode;
  setCorrMode: (m: CorrMode) => void;
}) {
  const [showInfo, setShowInfo] = useState(false);
  const info = CORR_INFO[corrMode];

  return (
    <div style={{
      padding: "8px 14px",
      borderTop: `1px solid ${colors.border}`,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: 6,
    }}>
      {/* Mode toggle + info button */}
      <div style={{ display: "flex", alignItems: "center", gap: 4, flexWrap: "wrap", justifyContent: "center" }}>
        {([["correlation", "\u0394Cov"], ["concurrence", "Concurrence"], ["tangle", "Tangle"]] as const).map(([mode, label]) => (
          <button
            key={mode}
            onClick={() => { setCorrMode(mode); setShowInfo(false); }}
            style={{
              background: corrMode === mode ? colors.accentDim : "transparent",
              color: corrMode === mode ? colors.accentLight : colors.textTertiary,
              border: `1px solid ${corrMode === mode ? colors.accent : "transparent"}`,
              borderRadius: 4,
              padding: "2px 8px",
              fontSize: 10,
              fontFamily: fonts.sans,
              cursor: "pointer",
              fontWeight: corrMode === mode ? 600 : 400,
            }}
          >
            {label}
          </button>
        ))}
        <button
          onClick={() => setShowInfo((v) => !v)}
          title="What does this mean?"
          style={{
            background: showInfo ? colors.accentDim : "transparent",
            color: showInfo ? colors.accentLight : colors.textTertiary,
            border: `1px solid ${showInfo ? colors.accent : colors.border}`,
            borderRadius: "50%",
            width: 20,
            height: 20,
            fontSize: 11,
            fontWeight: 700,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 0,
            marginLeft: 2,
            fontFamily: fonts.sans,
          }}
        >
          ?
        </button>
      </div>

      {/* Info tooltip */}
      {showInfo && (
        <div style={{
          background: colors.card,
          border: `1px solid ${colors.border}`,
          borderRadius: 8,
          padding: 12,
          maxWidth: 280,
        }}>
          <div style={{
            fontSize: 11,
            fontWeight: 700,
            color: colors.accentLight,
            marginBottom: 6,
            fontFamily: fonts.sans,
          }}>
            {info.title}
          </div>
          <p style={{
            fontSize: 11,
            color: colors.text,
            lineHeight: 1.5,
            margin: "0 0 8px",
            fontFamily: fonts.sans,
          }}>
            {info.explanation}
          </p>
          <div style={{
            fontSize: 10,
            color: colors.textSecondary,
            fontFamily: fonts.mono,
            background: colors.bg,
            padding: "4px 8px",
            borderRadius: 4,
            marginBottom: 8,
          }}>
            {info.formula}
          </div>
          <div style={{
            fontSize: 10,
            color: colors.textTertiary,
            lineHeight: 1.5,
            fontFamily: fonts.sans,
            borderTop: `1px solid ${colors.border}`,
            paddingTop: 6,
          }}>
            <span style={{ fontWeight: 600, color: colors.textSecondary }}>Example: </span>
            {info.example}
          </div>
        </div>
      )}

      {/* Matrix views */}
      {corrMode !== "tangle" && (
        <CorrelationHeatmap data={correlations} numQubits={numQubits} mode={corrMode} />
      )}

      {/* Tangle view */}
      {corrMode === "tangle" && (
        <TangleDisplay data={correlations} numQubits={numQubits} />
      )}
    </div>
  );
}

function TangleDisplay({ data, numQubits }: { data: import("../hooks/usePlayback").CorrelationData; numQubits: number }) {
  const tangleVal = data.tangle;
  const oneTangles = data.oneTangles;

  // Color: 0 = dark, 1 = bright gold/amber
  const tangleColor = (v: number) => {
    const t = Math.min(Math.max(v, 0), 1);
    if (t < 0.001) return colors.card;
    const r = Math.round(30 + 225 * t);
    const g = Math.round(30 + 130 * t);
    const b = Math.round(46 - 10 * t);
    return `rgb(${r},${g},${b})`;
  };

  // Classify the entanglement structure
  let classification = "";
  const maxPairC = Math.max(...data.concurrences.flat());
  if (tangleVal > 0.5 && maxPairC < 0.1) {
    classification = "Genuinely multipartite \u2014 entanglement cannot be reduced to pairs";
  } else if (tangleVal < 0.05 && maxPairC > 0.3) {
    classification = "Pairwise entanglement only \u2014 no genuinely multipartite component";
  } else if (tangleVal > 0.1 && maxPairC > 0.1) {
    classification = "Mixed structure \u2014 both pairwise and multipartite entanglement present";
  } else if (tangleVal < 0.05 && maxPairC < 0.05) {
    classification = "No significant entanglement \u2014 product state or classical correlations only";
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, width: "100%" }}>
      {/* Main tangle gauge */}
      <div style={{ textAlign: "center" }}>
        <div style={{
          fontSize: 10,
          color: colors.textTertiary,
          fontFamily: fonts.sans,
          marginBottom: 4,
          textTransform: "uppercase",
          letterSpacing: "0.5px",
        }}>
          {numQubits === 3 ? "3-Tangle (\u03C4\u2083)" : `Residual Tangle (${numQubits}Q)`}
        </div>
        <div style={{
          fontSize: 28,
          fontWeight: 700,
          fontFamily: fonts.mono,
          color: tangleVal > 0.01 ? tangleColor(tangleVal) : colors.textTertiary,
          lineHeight: 1,
        }}>
          {tangleVal.toFixed(3)}
        </div>
        <div style={{
          width: "100%",
          height: 6,
          borderRadius: 3,
          background: colors.card,
          marginTop: 6,
          overflow: "hidden",
        }}>
          <div style={{
            width: `${Math.min(tangleVal * 100, 100)}%`,
            height: "100%",
            borderRadius: 3,
            background: tangleColor(tangleVal),
            transition: "width 0.3s ease, background 0.3s ease",
          }} />
        </div>
      </div>

      {/* Per-qubit 1-tangles */}
      <div style={{ width: "100%" }}>
        <div style={{
          fontSize: 9,
          color: colors.textTertiary,
          fontFamily: fonts.sans,
          marginBottom: 4,
          textTransform: "uppercase",
          letterSpacing: "0.5px",
        }}>
          Per-qubit entanglement with rest
        </div>
        <div style={{ display: "flex", gap: 4, justifyContent: "center" }}>
          {oneTangles.map((ot, i) => (
            <div key={i} style={{
              flex: 1,
              maxWidth: 60,
              textAlign: "center",
            }}>
              <div style={{
                fontSize: 11,
                fontFamily: fonts.mono,
                fontWeight: 600,
                color: ot > 0.01 ? tangleColor(ot) : colors.textTertiary,
              }}>
                {ot.toFixed(2)}
              </div>
              <div style={{
                height: 4,
                borderRadius: 2,
                background: colors.card,
                marginTop: 2,
                overflow: "hidden",
              }}>
                <div style={{
                  width: `${Math.min(ot * 100, 100)}%`,
                  height: "100%",
                  borderRadius: 2,
                  background: tangleColor(ot),
                  transition: "width 0.3s ease",
                }} />
              </div>
              <div style={{ fontSize: 8, color: colors.textTertiary, fontFamily: fonts.mono, marginTop: 2 }}>
                q{i}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Classification */}
      {classification && (
        <div style={{
          fontSize: 10,
          color: colors.textSecondary,
          fontFamily: fonts.sans,
          textAlign: "center",
          lineHeight: 1.4,
          padding: "4px 8px",
          background: `${colors.card}`,
          borderRadius: 4,
          width: "100%",
        }}>
          {classification}
        </div>
      )}
    </div>
  );
}

function TransportButton({
  onClick, disabled, title, accent, children,
}: {
  onClick: () => void;
  disabled: boolean;
  title: string;
  accent?: boolean;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      style={{
        width: 36,
        height: 32,
        borderRadius: 6,
        border: `1px solid ${accent ? colors.accent : colors.border}`,
        background: accent ? colors.accentDim : colors.card,
        color: disabled ? colors.textTertiary : (accent ? colors.accentLight : colors.text),
        fontSize: 14,
        cursor: disabled ? "not-allowed" : "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity: disabled ? 0.4 : 1,
      }}
    >
      {children}
    </button>
  );
}
