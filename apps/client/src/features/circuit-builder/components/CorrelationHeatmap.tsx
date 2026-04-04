"use dom";

import type { CorrelationData } from "../hooks/usePlayback";
import { colors, fonts } from "../styles";

interface CorrelationHeatmapProps {
  data: CorrelationData;
  numQubits: number;
  /** Which matrix to display */
  mode: "correlation" | "concurrence";
}

/** Map value [-1, 1] to a color. Blue = negative, dark = zero, red/orange = positive */
function correlationColor(v: number): string {
  const abs = Math.min(Math.abs(v), 1);
  if (v > 0.001) {
    // Positive: orange/amber
    const r = Math.round(99 + 156 * abs);
    const g = Math.round(102 - 40 * abs);
    const b = Math.round(241 - 200 * abs);
    return `rgb(${r},${g},${b})`;
  } else if (v < -0.001) {
    // Negative: blue/cyan
    const r = Math.round(99 - 60 * abs);
    const g = Math.round(102 + 100 * abs);
    const b = Math.round(241);
    return `rgb(${r},${g},${b})`;
  }
  // Near zero: dark
  return colors.card;
}

/** Map value [0, 1] to concurrence color. Dark = 0, bright magenta = 1 */
function concurrenceColor(v: number): string {
  const abs = Math.min(Math.max(v, 0), 1);
  if (abs < 0.001) return colors.card;
  const r = Math.round(30 + 214 * abs);
  const g = Math.round(30 + 82 * abs);
  const b = Math.round(46 + 130 * abs);
  return `rgb(${r},${g},${b})`;
}

export default function CorrelationHeatmap({ data, numQubits, mode }: CorrelationHeatmapProps) {
  const matrix = mode === "correlation" ? data.deltaCov : data.concurrences;
  const colorFn = mode === "correlation" ? correlationColor : concurrenceColor;
  const cellSize = numQubits <= 4 ? 36 : numQubits <= 6 ? 28 : 22;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      {/* Grid */}
      <div style={{ display: "flex", gap: 0 }}>
        {/* Row labels */}
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "flex-end", marginRight: 2 }}>
          {Array.from({ length: numQubits }, (_, i) => (
            <div key={i} style={{
              height: cellSize,
              display: "flex",
              alignItems: "center",
              justifyContent: "flex-end",
              paddingRight: 4,
            }}>
              <span style={{ fontSize: 9, color: colors.textTertiary, fontFamily: fonts.mono }}>
                q{i}
              </span>
            </div>
          ))}
        </div>

        <div>
          {/* Column labels */}
          <div style={{ display: "flex", marginBottom: 2 }}>
            {Array.from({ length: numQubits }, (_, j) => (
              <div key={j} style={{
                width: cellSize,
                textAlign: "center",
              }}>
                <span style={{ fontSize: 9, color: colors.textTertiary, fontFamily: fonts.mono }}>
                  q{j}
                </span>
              </div>
            ))}
          </div>

          {/* Matrix cells */}
          {matrix.map((row, i) => (
            <div key={i} style={{ display: "flex" }}>
              {row.map((val, j) => {
                const isDiag = i === j && mode === "concurrence";
                return (
                  <div
                    key={j}
                    title={`q${i},q${j}: ${val.toFixed(4)}`}
                    style={{
                      width: cellSize,
                      height: cellSize,
                      background: isDiag ? "transparent" : colorFn(val),
                      border: `1px solid ${colors.bg}`,
                      borderRadius: 3,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      transition: "background 0.2s ease",
                    }}
                  >
                    {!isDiag && Math.abs(val) > 0.005 && (
                      <span style={{
                        fontSize: numQubits <= 4 ? 9 : 7,
                        color: Math.abs(val) > 0.3 ? "#fff" : colors.textTertiary,
                        fontFamily: fonts.mono,
                        fontWeight: Math.abs(val) > 0.5 ? 700 : 400,
                      }}>
                        {val > 0 ? "+" : ""}{val.toFixed(2)}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Scale legend */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 4,
        marginTop: 2,
      }}>
        {mode === "correlation" ? (
          <>
            <span style={{ fontSize: 8, color: colors.textTertiary, fontFamily: fonts.mono }}>\u22121</span>
            <div style={{
              width: 60, height: 6, borderRadius: 3,
              background: "linear-gradient(to right, rgb(39,202,241), rgb(30,30,46), rgb(255,62,41))",
            }} />
            <span style={{ fontSize: 8, color: colors.textTertiary, fontFamily: fonts.mono }}>+1</span>
          </>
        ) : (
          <>
            <span style={{ fontSize: 8, color: colors.textTertiary, fontFamily: fonts.mono }}>0</span>
            <div style={{
              width: 60, height: 6, borderRadius: 3,
              background: `linear-gradient(to right, ${colors.card}, rgb(244,112,176))`,
            }} />
            <span style={{ fontSize: 8, color: colors.textTertiary, fontFamily: fonts.mono }}>1</span>
          </>
        )}
      </div>
    </div>
  );
}
