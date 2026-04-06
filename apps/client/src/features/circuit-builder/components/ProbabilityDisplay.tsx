import { useState } from "react";
import { colors, fonts } from "../styles";
import type { SimSnapshot } from "../types";

interface ProbabilityDisplayProps {
  snapshot: SimSnapshot | null;
}

/** Max items to show before collapsing; only non-zero probabilities shown. */
const MAX_VISIBLE = 16;

export default function ProbabilityDisplay({ snapshot }: ProbabilityDisplayProps) {
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
        Add gates to see measurement probabilities
      </div>
    );
  }

  const { probabilities, labels } = snapshot;
  const maxProb = Math.max(...probabilities, 0.01);

  // Build entries with index, filter out near-zero, sort by probability desc
  const entries = labels
    .map((label, i) => ({ label, prob: probabilities[i] }))
    .filter((e) => e.prob > 0.0005)
    .sort((a, b) => b.prob - a.prob);

  const totalNonZero = entries.length;
  const visible = showAll ? entries : entries.slice(0, MAX_VISIBLE);
  const hasMore = totalNonZero > MAX_VISIBLE && !showAll;

  return (
    <div style={{
      padding: "12px",
      background: colors.surface,
      borderRadius: 8,
      border: `1px solid ${colors.border}`,
      maxHeight: 300,
      overflowY: "auto",
    }}>
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
          Measurement Probabilities
        </span>
        {totalNonZero > 0 && (
          <span style={{ color: colors.textTertiary, fontSize: 10, fontFamily: fonts.mono }}>
            {totalNonZero} outcome{totalNonZero !== 1 ? "s" : ""}
          </span>
        )}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {visible.map(({ label, prob }) => {
          const pct = prob * 100;
          const barWidth = (prob / maxProb) * 100;
          return (
            <div
              key={label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <span
                style={{
                  width: 56,
                  color: colors.textSecondary,
                  fontSize: 12,
                  fontFamily: fonts.mono,
                  textAlign: "right",
                  flexShrink: 0,
                }}
              >
                {label}
              </span>
              <div
                style={{
                  flex: 1,
                  height: 18,
                  background: colors.card,
                  borderRadius: 4,
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${barWidth}%`,
                    height: "100%",
                    background: `linear-gradient(90deg, ${colors.accent}, ${colors.accentLight})`,
                    borderRadius: 4,
                    transition: "width 0.3s ease",
                  }}
                />
              </div>
              <span
                style={{
                  width: 48,
                  color: colors.text,
                  fontSize: 12,
                  fontFamily: fonts.mono,
                  textAlign: "right",
                  flexShrink: 0,
                }}
              >
                {pct.toFixed(1)}%
              </span>
            </div>
          );
        })}
      </div>
      {hasMore && (
        <div
          onClick={() => setShowAll(true)}
          style={{
            color: colors.accent,
            fontSize: 11,
            fontWeight: 600,
            cursor: "pointer",
            textAlign: "center",
            marginTop: 8,
            padding: 4,
          }}
        >
          Show all {totalNonZero} outcomes
        </div>
      )}
    </div>
  );
}
