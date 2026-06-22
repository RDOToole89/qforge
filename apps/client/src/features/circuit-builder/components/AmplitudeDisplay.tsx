import { useState } from "react";
import { viz } from "@/src/design/tokens";
import { colors, fonts, lighten } from "../styles";
import type { SimSnapshot } from "../types";

interface AmplitudeDisplayProps {
  snapshot: SimSnapshot | null;
  /** All snapshots for the evolution graph */
  allSnapshots?: SimSnapshot[];
  /** Current step index for highlighting on the evolution graph */
  currentStep?: number;
  /** Continuous playback progress 0..1 for the playhead */
  playbackProgress?: number;
  /** Gate labels per moment for the evolution graph header */
  gateLabels?: string[];
}

const MAX_VISIBLE = 16;

/**
 * Map a complex phase angle [0, 2π) to a color.
 * 0° = blue (positive real), 90° = green (positive imag),
 * 180° = red (negative real), 270° = purple (negative imag).
 * Standard quantum optics convention.
 */
function phaseColor(angle: number): string {
  // Normalize to [0, 360)
  const deg = ((angle * 180 / Math.PI) % 360 + 360) % 360;
  // Map to hue: 0° → 220 (blue), 90° → 140 (green), 180° → 0 (red), 270° → 280 (purple)
  const hue = (220 - deg * 220 / 360 + 360) % 360;
  return `hsl(${hue}, 75%, 60%)`;
}

function formatAngle(radians: number): string {
  const deg = ((radians * 180 / Math.PI) % 360 + 360) % 360;
  // Common angles
  if (Math.abs(deg - 0) < 1 || Math.abs(deg - 360) < 1) return "0\u00B0";
  if (Math.abs(deg - 90) < 1) return "90\u00B0";
  if (Math.abs(deg - 180) < 1) return "180\u00B0";
  if (Math.abs(deg - 270) < 1) return "270\u00B0";
  if (Math.abs(deg - 45) < 1) return "45\u00B0";
  if (Math.abs(deg - 135) < 1) return "135\u00B0";
  if (Math.abs(deg - 225) < 1) return "225\u00B0";
  if (Math.abs(deg - 315) < 1) return "315\u00B0";
  return `${deg.toFixed(0)}\u00B0`;
}

export default function AmplitudeDisplay({ snapshot, allSnapshots, currentStep, gateLabels, playbackProgress }: AmplitudeDisplayProps) {
  const [view, setView] = useState<"bars" | "evolution">("bars");
  const [mode, setMode] = useState<"magnitude" | "complex">("magnitude");
  const [showAll, setShowAll] = useState(false);

  if (!snapshot) {
    return (
      <div style={{
        padding: "16px 12px",
        background: colors.surface,
        borderRadius: 8,
        border: `1px solid ${colors.border}`,
        color: colors.textTertiary,
        fontSize: 13,
        fontFamily: fonts.sans,
        textAlign: "center",
      }}>
        Add gates to see quantum amplitudes
      </div>
    );
  }

  const { stateVector, labels } = snapshot;

  // Build entries with amplitude data
  const entries = labels.map((label, i) => {
    const [re, im] = stateVector[i];
    const magnitude = Math.sqrt(re * re + im * im);
    const phase = Math.atan2(im, re);
    const prob = re * re + im * im;
    return { label, re, im, magnitude, phase, prob, index: i };
  }).filter((e) => e.magnitude > 0.0005);

  const maxMagnitude = Math.max(...entries.map((e) => e.magnitude), 0.01);
  const totalNonZero = entries.length;
  const visible = showAll ? entries : entries.slice(0, MAX_VISIBLE);
  const hasMore = totalNonZero > MAX_VISIBLE && !showAll;

  return (
    <div style={{
      padding: "12px",
      background: colors.surface,
      borderRadius: 8,
      border: `1px solid ${colors.border}`,
      display: "flex",
      flexDirection: "column",
      flex: 1,
      minHeight: 0,
    }}>
      {/* Header with view selector */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: 8,
      }}>
        <span style={{
          color: colors.textSecondary,
          fontSize: 11,
          fontWeight: 600,
          fontFamily: fonts.sans,
          textTransform: "uppercase",
          letterSpacing: "0.5px",
        }}>
          Quantum Amplitudes
        </span>
        <div style={{ display: "flex", gap: 2 }}>
          {([["bars", "Bars"], ["evolution", "Evolution"]] as const).map(([v, label]) => (
            <button
              key={v}
              onClick={() => setView(v)}
              style={{
                background: view === v ? colors.accentDim : "transparent",
                color: view === v ? colors.accentLight : colors.textTertiary,
                border: `1px solid ${view === v ? colors.accent : "transparent"}`,
                borderRadius: 4,
                padding: "1px 6px",
                fontSize: 9,
                fontFamily: fonts.sans,
                cursor: "pointer",
                fontWeight: view === v ? 600 : 400,
              }}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Bar chart view */}
      {view === "bars" && (
        <>
          <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 4 }}>
            {([["magnitude", "|\u03B1| + \u2220"], ["complex", "Re + Im"]] as const).map(([m, label]) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                style={{
                  background: mode === m ? colors.accentDim : "transparent",
                  color: mode === m ? colors.accentLight : colors.textTertiary,
                  border: `1px solid ${mode === m ? colors.accent : "transparent"}`,
                  borderRadius: 4,
                  padding: "1px 6px",
                  fontSize: 8,
                  fontFamily: fonts.mono,
                  cursor: "pointer",
                  fontWeight: mode === m ? 600 : 400,
                  marginLeft: 2,
                }}
              >
                {label}
              </button>
            ))}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {visible.map((entry) => (
              mode === "magnitude"
                ? <MagnitudeRow key={entry.label} entry={entry} maxMagnitude={maxMagnitude} />
                : <ComplexRow key={entry.label} entry={entry} />
            ))}
          </div>
          {hasMore && (
            <div onClick={() => setShowAll(true)} style={{
              color: colors.accent, fontSize: 11, fontWeight: 600,
              cursor: "pointer", textAlign: "center", marginTop: 8, padding: 4,
            }}>
              Show all {totalNonZero} amplitudes
            </div>
          )}
        </>
      )}

      {/* Evolution line graph view */}
      {view === "evolution" && allSnapshots && allSnapshots.length > 1 && (
        <div style={{ flex: 1, minHeight: 0 }}>
          <EvolutionGraph snapshots={allSnapshots} currentStep={currentStep ?? 0} gateLabels={gateLabels} playbackProgress={playbackProgress} />
        </div>
      )}
      {view === "evolution" && (!allSnapshots || allSnapshots.length <= 1) && (
        <div style={{ padding: 16, color: colors.textTertiary, fontSize: 12, textAlign: "center", fontFamily: fonts.sans }}>
          Add gates to see amplitude evolution across circuit steps
        </div>
      )}

      {/* Phase legend — only for bars view */}
      {view === "bars" && (
        <div style={{
          marginTop: 8,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 8,
          fontSize: 8,
          color: colors.textTertiary,
          fontFamily: fonts.mono,
          flexShrink: 0,
        }}>
          <span style={{ display: "flex", alignItems: "center", gap: 2 }}>
            <span style={{ width: 6, height: 6, borderRadius: 3, background: phaseColor(0) }} /> +Re
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: 2 }}>
            <span style={{ width: 6, height: 6, borderRadius: 3, background: phaseColor(Math.PI / 2) }} /> +Im
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: 2 }}>
            <span style={{ width: 6, height: 6, borderRadius: 3, background: phaseColor(Math.PI) }} /> -Re
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: 2 }}>
            <span style={{ width: 6, height: 6, borderRadius: 3, background: phaseColor(3 * Math.PI / 2) }} /> -Im
          </span>
        </div>
      )}
    </div>
  );
}

// ── Magnitude + Phase row ──

function MagnitudeRow({ entry, maxMagnitude }: {
  entry: { label: string; magnitude: number; phase: number; prob: number };
  maxMagnitude: number;
}) {
  const barWidth = (entry.magnitude / maxMagnitude) * 100;
  const pColor = phaseColor(entry.phase);

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      {/* Label */}
      <span style={{
        width: 50,
        color: colors.textSecondary,
        fontSize: 11,
        fontFamily: fonts.mono,
        textAlign: "right",
        flexShrink: 0,
      }}>
        {entry.label}
      </span>

      {/* Magnitude bar */}
      <div style={{
        flex: 1,
        height: 18,
        background: colors.bg,
        borderRadius: 4,
        overflow: "hidden",
      }}>
        <div style={{
          width: `${barWidth}%`,
          height: "100%",
          background: entry.phase > Math.PI / 2 && entry.phase < 3 * Math.PI / 2
            ? `linear-gradient(90deg, ${colors.danger}, ${lighten(colors.danger, 0.32)})` // red for negative real
            : `linear-gradient(90deg, ${colors.accent}, ${colors.accentLight})`, // blue for positive
          borderRadius: 4,
          transition: "width 0.3s ease",
          minWidth: barWidth > 0 ? 4 : 0,
        }} />
      </div>

      {/* Magnitude value */}
      <span style={{
        width: 32,
        color: colors.text,
        fontSize: 10,
        fontFamily: fonts.mono,
        textAlign: "right",
        flexShrink: 0,
      }}>
        {entry.magnitude.toFixed(2)}
      </span>

      {/* Phase circle */}
      <PhaseCircle angle={entry.phase} size={14} />

      {/* Phase angle */}
      <span style={{
        width: 30,
        color: colors.textTertiary,
        fontSize: 9,
        fontFamily: fonts.mono,
        flexShrink: 0,
      }}>
        {formatAngle(entry.phase)}
      </span>
    </div>
  );
}

// ── Real + Imaginary row ──

function ComplexRow({ entry }: {
  entry: { label: string; re: number; im: number; magnitude: number };
}) {
  const maxVal = Math.max(Math.abs(entry.re), Math.abs(entry.im), 0.01);
  // Scale relative to 1.0 (max possible amplitude)
  const reBarWidth = Math.abs(entry.re) * 50; // 50% = magnitude 1.0
  const imBarWidth = Math.abs(entry.im) * 50;

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      {/* Label */}
      <span style={{
        width: 50,
        color: colors.textSecondary,
        fontSize: 11,
        fontFamily: fonts.mono,
        textAlign: "right",
        flexShrink: 0,
      }}>
        {entry.label}
      </span>

      {/* Re/Im bars container — centered, with bars extending left (negative) or right (positive) */}
      <div style={{ flex: 1, display: "flex", gap: 2 }}>
        {/* Real part */}
        <div style={{
          flex: 1,
          height: 14,
          display: "flex",
          alignItems: "center",
          position: "relative",
        }}>
          <div style={{
            position: "absolute",
            left: "50%",
            top: 0,
            bottom: 0,
            width: 1,
            background: colors.border,
          }} />
          {entry.re !== 0 && (
            <div style={{
              position: "absolute",
              [entry.re >= 0 ? "left" : "right"]: "50%",
              width: `${reBarWidth}%`,
              height: 12,
              background: entry.re >= 0 ? "hsl(220, 75%, 60%)" : "hsl(0, 75%, 60%)",
              borderRadius: 2,
              transition: "width 0.3s ease",
            }} />
          )}
        </div>

        {/* Imaginary part */}
        <div style={{
          flex: 1,
          height: 14,
          display: "flex",
          alignItems: "center",
          position: "relative",
        }}>
          <div style={{
            position: "absolute",
            left: "50%",
            top: 0,
            bottom: 0,
            width: 1,
            background: colors.border,
          }} />
          {entry.im !== 0 && (
            <div style={{
              position: "absolute",
              [entry.im >= 0 ? "left" : "right"]: "50%",
              width: `${imBarWidth}%`,
              height: 12,
              background: entry.im >= 0 ? "hsl(140, 75%, 60%)" : "hsl(280, 75%, 60%)",
              borderRadius: 2,
              transition: "width 0.3s ease",
            }} />
          )}
        </div>
      </div>

      {/* Values */}
      <span style={{
        width: 70,
        color: colors.textSecondary,
        fontSize: 9,
        fontFamily: fonts.mono,
        flexShrink: 0,
      }}>
        {entry.re >= 0 ? "+" : ""}{entry.re.toFixed(2)} {entry.im >= 0 ? "+" : ""}{entry.im.toFixed(2)}i
      </span>
    </div>
  );
}

// ── Phase circle indicator ──

function PhaseCircle({ angle, size = 14 }: { angle: number; size?: number }) {
  const r = size / 2;
  const lineX = r + (r - 2) * Math.cos(angle);
  const lineY = r - (r - 2) * Math.sin(angle);

  return (
    <svg width={size} height={size} style={{ flexShrink: 0 }}>
      <circle cx={r} cy={r} r={r - 1} fill="none" stroke={colors.border} strokeWidth={1} />
      <line x1={r} y1={r} x2={lineX} y2={lineY}
        stroke={phaseColor(angle)} strokeWidth={1.5} strokeLinecap="round" />
      <circle cx={lineX} cy={lineY} r={1.5} fill={phaseColor(angle)} />
    </svg>
  );
}

// ═══════════════════════════════════════════════════════════════
// PHASOR DIAGRAM — rotating arrows in the complex plane
// ═══════════════════════════════════════════════════════════════

const PHASOR_COLORS = [
  viz.gate.indigo, viz.gate.red, viz.gate.green, viz.gate.amber,
  viz.gate.pink, viz.gate.teal, viz.gate.violet, viz.gate.orange,
  viz.cyanDeep, viz.lime, viz.crimson, viz.azure,
  viz.gate.purple, viz.gate.yellow, colors.textTertiary, viz.amber,
];

function PhasorDiagram({ entries }: {
  entries: { label: string; re: number; im: number; magnitude: number; phase: number }[];
}) {
  const size = 400;
  const cx = size / 2;
  const cy = size / 2;
  const radius = size / 2 - 40;

  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0, gap: 6 }}>
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${size} ${size}`}
        preserveAspectRatio="xMidYMid meet"
        style={{ background: colors.card, borderRadius: 8, flex: 1, minHeight: 0 }}
      >
        {/* Grid circles with labels */}
        {[0.25, 0.5, 0.75, 1.0].map((r) => (
          <g key={r}>
            <circle cx={cx} cy={cy} r={radius * r}
              fill="none" stroke={colors.border} strokeWidth={0.5} opacity={0.3} />
            <text x={cx + radius * r + 2} y={cy - 3} fill={colors.textTertiary}
              fontSize={9} fontFamily={fonts.mono} opacity={0.5}>
              {r.toFixed(2)}
            </text>
          </g>
        ))}

        {/* Axes */}
        <line x1={cx - radius - 10} y1={cy} x2={cx + radius + 10} y2={cy}
          stroke={colors.border} strokeWidth={0.5} opacity={0.4} />
        <line x1={cx} y1={cy - radius - 10} x2={cx} y2={cy + radius + 10}
          stroke={colors.border} strokeWidth={0.5} opacity={0.4} />

        {/* Axis labels */}
        <text x={cx + radius + 14} y={cy + 4} fill={colors.textSecondary}
          fontSize={12} fontFamily={fonts.mono}>+Re</text>
        <text x={cx - radius - 30} y={cy + 4} fill={colors.textSecondary}
          fontSize={12} fontFamily={fonts.mono}>\u2212Re</text>
        <text x={cx + 4} y={cy - radius - 14} fill={colors.textSecondary}
          fontSize={12} fontFamily={fonts.mono}>+Im</text>
        <text x={cx + 4} y={cy + radius + 22} fill={colors.textSecondary}
          fontSize={12} fontFamily={fonts.mono}>\u2212Im</text>

        {/* Quadrant labels */}
        <text x={cx + radius * 0.5} y={cy - radius * 0.5} fill={colors.textTertiary}
          fontSize={9} fontFamily={fonts.sans} opacity={0.3} textAnchor="middle">
          0\u00B0\u201390\u00B0
        </text>
        <text x={cx - radius * 0.5} y={cy - radius * 0.5} fill={colors.textTertiary}
          fontSize={9} fontFamily={fonts.sans} opacity={0.3} textAnchor="middle">
          90\u00B0\u2013180\u00B0
        </text>

        {/* Phasor arrows */}
        {entries.map((entry, i) => {
          if (entry.magnitude < 0.001) return null;
          const endX = cx + entry.re * radius;
          const endY = cy - entry.im * radius;
          const color = PHASOR_COLORS[i % PHASOR_COLORS.length];

          return (
            <g key={entry.label}>
              {/* Faint projection lines to axes */}
              <line x1={endX} y1={endY} x2={endX} y2={cy}
                stroke={color} strokeWidth={0.5} strokeDasharray="2 2" opacity={0.3} />
              <line x1={endX} y1={endY} x2={cx} y2={endY}
                stroke={color} strokeWidth={0.5} strokeDasharray="2 2" opacity={0.3} />

              {/* Arrow line */}
              <line x1={cx} y1={cy} x2={endX} y2={endY}
                stroke={color} strokeWidth={2.5} strokeLinecap="round" />
              {/* Arrow head dot */}
              <circle cx={endX} cy={endY} r={5} fill={color} />
              {/* Magnitude arc */}
              {entry.magnitude > 0.05 && entry.phase !== 0 && (
                <path
                  d={`M ${cx + 20} ${cy} A 20 20 0 ${Math.abs(entry.phase) > Math.PI ? 1 : 0} ${entry.phase >= 0 ? 0 : 1} ${cx + 20 * Math.cos(entry.phase)} ${cy - 20 * Math.sin(entry.phase)}`}
                  fill="none"
                  stroke={color}
                  strokeWidth={1}
                  opacity={0.5}
                />
              )}
              {/* Label */}
              <text
                x={endX + (entry.re >= 0 ? 10 : -10)}
                y={endY + (entry.im >= 0 ? -10 : 14)}
                fill={color}
                fontSize={11}
                fontWeight={600}
                fontFamily={fonts.mono}
                textAnchor={entry.re >= 0 ? "start" : "end"}
              >
                {entry.label}
              </text>
              {/* Value */}
              <text
                x={endX + (entry.re >= 0 ? 10 : -10)}
                y={endY + (entry.im >= 0 ? 2 : 26)}
                fill={color}
                fontSize={9}
                fontFamily={fonts.mono}
                textAnchor={entry.re >= 0 ? "start" : "end"}
                opacity={0.7}
              >
                {entry.magnitude.toFixed(3)} \u2220{((entry.phase * 180 / Math.PI + 360) % 360).toFixed(0)}\u00B0
              </text>
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "4px 12px",
        justifyContent: "center",
        padding: "4px 8px",
        background: colors.surface,
        borderRadius: 6,
      }}>
        {entries.filter((e) => e.magnitude > 0.001).map((entry, i) => (
          <span key={entry.label} style={{
            display: "flex", alignItems: "center", gap: 4,
            fontSize: 10, fontFamily: fonts.mono, color: colors.text,
          }}>
            <span style={{
              width: 10, height: 3, borderRadius: 1,
              background: PHASOR_COLORS[i % PHASOR_COLORS.length],
            }} />
            {entry.label} = {entry.re.toFixed(3)} {entry.im >= 0 ? "+" : "\u2212"} {Math.abs(entry.im).toFixed(3)}i
          </span>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// EVOLUTION GRAPH — amplitude traces across circuit steps
// ═══════════════════════════════════════════════════════════════

function EvolutionGraph({ snapshots, currentStep, gateLabels, playbackProgress }: {
  snapshots: SimSnapshot[];
  currentStep: number;
  gateLabels?: string[];
  playbackProgress?: number;
}) {
  const [showGrid, setShowGrid] = useState(true);

  const width = 500;
  const height = 280;
  const padL = 32;
  const padR = 12;
  const padT = 14;
  const padB = gateLabels ? 44 : 24;
  const plotW = width - padL - padR;
  const plotH = height - padT - padB;

  const numSteps = snapshots.length;
  const dim = snapshots[0]?.stateVector.length ?? 0;
  if (numSteps < 2 || dim === 0) return null;

  const activeStates: number[] = [];
  for (let b = 0; b < dim; b++) {
    let has = false;
    for (let s = 0; s < numSteps; s++) {
      const [re, im] = snapshots[s].stateVector[b];
      if (re * re + im * im > 0.001) { has = true; break; }
    }
    if (has) activeStates.push(b);
  }

  const stepX = (s: number) => padL + (s / (numSteps - 1)) * plotW;
  const ampY = (v: number) => padT + plotH / 2 - v * (plotH / 2);

  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0, gap: 4 }}>
      {/* Grid toggle */}
      <div style={{ display: "flex", justifyContent: "flex-end", paddingRight: 4 }}>
        <button
          onClick={() => setShowGrid((v) => !v)}
          style={{
            background: showGrid ? colors.accentDim : "transparent",
            color: showGrid ? colors.accentLight : colors.textTertiary,
            border: `1px solid ${showGrid ? colors.accent : colors.border}`,
            borderRadius: 4,
            padding: "1px 6px",
            fontSize: 8,
            fontFamily: fonts.sans,
            cursor: "pointer",
          }}
        >
          Grid
        </button>
      </div>

      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="xMidYMid meet"
        style={{ background: colors.card, borderRadius: 8, flex: 1, minHeight: 0 }}
      >
        {/* Step grid lines (toggleable) */}
        {showGrid && Array.from({ length: numSteps }, (_, s) => (
          <line key={`grid-${s}`}
            x1={stepX(s)} y1={padT} x2={stepX(s)} y2={padT + plotH}
            stroke={colors.accentLight} strokeWidth={0.5} strokeDasharray="4 4" opacity={0.25}
          />
        ))}

        {/* Horizontal reference lines */}
        <line x1={padL} y1={ampY(0)} x2={padL + plotW} y2={ampY(0)}
          stroke={colors.border} strokeWidth={1} />
        <line x1={padL} y1={ampY(1)} x2={padL + plotW} y2={ampY(1)}
          stroke={colors.border} strokeWidth={0.5} strokeDasharray="2 4" opacity={0.3} />
        <line x1={padL} y1={ampY(-1)} x2={padL + plotW} y2={ampY(-1)}
          stroke={colors.border} strokeWidth={0.5} strokeDasharray="2 4" opacity={0.3} />
        <line x1={padL} y1={ampY(0.5)} x2={padL + plotW} y2={ampY(0.5)}
          stroke={colors.border} strokeWidth={0.3} strokeDasharray="1 3" opacity={0.2} />
        <line x1={padL} y1={ampY(-0.5)} x2={padL + plotW} y2={ampY(-0.5)}
          stroke={colors.border} strokeWidth={0.3} strokeDasharray="1 3" opacity={0.2} />

        {/* Y-axis labels */}
        <text x={padL - 4} y={ampY(1) + 3} fill={colors.textTertiary}
          fontSize={8} fontFamily={fonts.mono} textAnchor="end">+1</text>
        <text x={padL - 4} y={ampY(0) + 3} fill={colors.textTertiary}
          fontSize={8} fontFamily={fonts.mono} textAnchor="end">0</text>
        <text x={padL - 4} y={ampY(-1) + 3} fill={colors.textTertiary}
          fontSize={8} fontFamily={fonts.mono} textAnchor="end">-1</text>

        {/* Step numbers at bottom */}
        {Array.from({ length: numSteps }, (_, s) => (
          <text key={s} x={stepX(s)} y={padT + plotH + 14} fill={colors.textSecondary}
            fontSize={9} fontFamily={fonts.mono} textAnchor="middle">
            {s}
          </text>
        ))}

        {/* Gate labels below step numbers */}
        {gateLabels && gateLabels.map((label, s) => (
          <text key={`gate-${s}`}
            x={(stepX(s) + stepX(s + 1)) / 2}
            y={padT + plotH + 28}
            fill={colors.accentLight}
            fontSize={8}
            fontFamily={fonts.mono}
            textAnchor="middle"
          >
            {label}
          </text>
        ))}

        {/* Playhead — moves continuously with playback */}
        {(() => {
          const px = playbackProgress !== undefined
            ? padL + playbackProgress * plotW
            : stepX(currentStep);
          return (
            <g>
              {/* Glow */}
              <line x1={px} y1={padT} x2={px} y2={padT + plotH}
                stroke={colors.accent} strokeWidth={4} opacity={0.15} />
              {/* Main line */}
              <line x1={px} y1={padT - 4} x2={px} y2={padT + plotH + 4}
                stroke={colors.accent} strokeWidth={2} strokeLinecap="round" />
              {/* Top triangle marker */}
              <polygon
                points={`${px - 4},${padT - 4} ${px + 4},${padT - 4} ${px},${padT + 2}`}
                fill={colors.accent}
              />
            </g>
          );
        })()}

        {/* Amplitude traces — real parts as solid lines */}
        {activeStates.map((b, idx) => {
          const color = PHASOR_COLORS[idx % PHASOR_COLORS.length];
          const points = snapshots.map((snap, s) =>
            `${stepX(s)},${ampY(snap.stateVector[b][0])}`
          ).join(" ");

          return (
            <g key={b}>
              <polyline points={points} fill="none"
                stroke={color} strokeWidth={2} strokeLinejoin="round" />
              {snapshots.map((snap, s) => (
                <circle key={s}
                  cx={stepX(s)} cy={ampY(snap.stateVector[b][0])}
                  r={s === currentStep ? 4 : 2}
                  fill={color}
                  opacity={s === currentStep ? 1 : 0.7}
                />
              ))}
            </g>
          );
        })}

        {/* Imaginary parts — dashed lines */}
        {activeStates.map((b, idx) => {
          const color = PHASOR_COLORS[idx % PHASOR_COLORS.length];
          const hasImag = snapshots.some((snap) => Math.abs(snap.stateVector[b][1]) > 0.001);
          if (!hasImag) return null;

          const points = snapshots.map((snap, s) =>
            `${stepX(s)},${ampY(snap.stateVector[b][1])}`
          ).join(" ");

          return (
            <polyline key={`im-${b}`} points={points} fill="none"
              stroke={color} strokeWidth={1.5} strokeDasharray="4 3"
              strokeLinejoin="round" opacity={0.5} />
          );
        })}
      </svg>

      {/* Legend — larger, clearer */}
      <div style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "4px 12px",
        justifyContent: "center",
        padding: "4px 8px",
        background: colors.surface,
        borderRadius: 6,
      }}>
        {activeStates.map((b, idx) => (
          <span key={b} style={{
            display: "flex", alignItems: "center", gap: 4,
            fontSize: 10, fontFamily: fonts.mono, color: colors.text,
          }}>
            <span style={{
              width: 10, height: 3, borderRadius: 1,
              background: PHASOR_COLORS[idx % PHASOR_COLORS.length],
            }} />
            {snapshots[0].labels[b]}
          </span>
        ))}
        <span style={{
          color: colors.textTertiary, fontFamily: fonts.sans, fontSize: 9,
          marginLeft: 8, display: "flex", alignItems: "center", gap: 4,
        }}>
          <span style={{ width: 10, height: 0, borderTop: `2px solid ${colors.textTertiary}` }} /> Re
          <span style={{ width: 10, height: 0, borderTop: `2px dashed ${colors.textTertiary}` }} /> Im
        </span>
      </div>
    </div>
  );
}
