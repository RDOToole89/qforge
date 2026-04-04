"use dom";

import { useState } from "react";
import UnifiedBlochSphere from "@/src/features/bloch-sphere/components/UnifiedBlochSphere";
import CorrelationHeatmap from "./CorrelationHeatmap";
import type { UsePlaybackReturn } from "../hooks/usePlayback";
import { colors, fonts } from "../styles";

interface BlochPlaybackPanelProps {
  playback: UsePlaybackReturn;
  numQubits: number;
}

const SPEED_OPTIONS = [0.25, 0.5, 1, 2, 4];

export default function BlochPlaybackPanel({ playback, numQubits }: BlochPlaybackPanelProps) {
  const [fullscreen, setFullscreen] = useState(false);
  const [corrMode, setCorrMode] = useState<"correlation" | "concurrence">("correlation");
  const { state, play, pause, stepBack, stepForward, setSpeed, reset, totalSnapshots } = playback;
  const { status, snapshotIndex, speed, dots, correlations } = state;

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
          <span>Bloch Sphere</span>
          <button
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

        {/* Sphere */}
        <div style={{
          flex: 1,
          minHeight: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 8,
        }}>
          {hasCircuit ? (
            <UnifiedBlochSphere mode="circuit" dots={dots} size={260} />
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

        <QubitLegend dots={dots} hasCircuit={hasCircuit} />

        {/* Correlation heatmap */}
        {hasCircuit && correlations && numQubits >= 2 && (
          <CorrelationPanel correlations={correlations} numQubits={numQubits} corrMode={corrMode} setCorrMode={setCorrMode} />
        )}

        <TransportControls
          hasCircuit={hasCircuit}
          status={status}
          snapshotIndex={snapshotIndex}
          totalSnapshots={totalSnapshots}
          speed={speed}
          play={play}
          pause={pause}
          stepBack={stepBack}
          stepForward={stepForward}
          setSpeed={setSpeed}
          reset={reset}
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
            <div style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: 24,
              minHeight: 400,
            }}>
              {hasCircuit ? (
                <UnifiedBlochSphere mode="circuit" dots={dots} size={520} />
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

            {/* Controls */}
            <div style={{ padding: "0 20px" }}>
              <QubitLegend dots={dots} hasCircuit={hasCircuit} />
            </div>
            {hasCircuit && correlations && numQubits >= 2 && (
              <div style={{ padding: "0 20px", display: "flex", justifyContent: "center" }}>
                <CorrelationPanel correlations={correlations} numQubits={numQubits} corrMode={corrMode} setCorrMode={setCorrMode} />
              </div>
            )}
            <div style={{ padding: "0 20px 16px" }}>
              <TransportControls
                hasCircuit={hasCircuit}
                status={status}
                snapshotIndex={snapshotIndex}
                totalSnapshots={totalSnapshots}
                speed={speed}
                play={play}
                pause={pause}
                stepBack={stepBack}
                stepForward={stepForward}
                setSpeed={setSpeed}
                reset={reset}
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
  play: () => void;
  pause: () => void;
  stepBack: () => void;
  stepForward: () => void;
  setSpeed: (s: number) => void;
  reset: () => void;
}

function TransportControls({
  hasCircuit, status, snapshotIndex, totalSnapshots,
  speed, play, pause, stepBack, stepForward, setSpeed, reset,
}: TransportControlsProps) {
  return (
    <div style={{
      padding: "8px 14px",
      borderTop: `1px solid ${colors.border}`,
      display: "flex",
      flexDirection: "column",
      gap: 6,
    }}>
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

function CorrelationPanel({
  correlations, numQubits, corrMode, setCorrMode,
}: {
  correlations: import("../hooks/usePlayback").CorrelationData;
  numQubits: number;
  corrMode: "correlation" | "concurrence";
  setCorrMode: (m: "correlation" | "concurrence") => void;
}) {
  return (
    <div style={{
      padding: "8px 14px",
      borderTop: `1px solid ${colors.border}`,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: 6,
    }}>
      {/* Mode toggle */}
      <div style={{ display: "flex", gap: 2 }}>
        {([["correlation", "\u0394Cov"], ["concurrence", "Concurrence"]] as const).map(([mode, label]) => (
          <button
            key={mode}
            onClick={() => setCorrMode(mode)}
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
      </div>
      <CorrelationHeatmap data={correlations} numQubits={numQubits} mode={corrMode} />
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
