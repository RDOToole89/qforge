import { colors, fonts } from "../styles";
import type { SimSnapshot } from "../types";

interface ProbabilityDisplayProps {
  snapshot: SimSnapshot | null;
}

export default function ProbabilityDisplay({ snapshot }: ProbabilityDisplayProps) {
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

  return (
    <div style={{
      padding: "12px",
      background: colors.surface,
      borderRadius: 8,
      border: `1px solid ${colors.border}`,
    }}>
      <div style={{
        color: colors.textSecondary,
        fontSize: 11,
        fontWeight: 600,
        fontFamily: fonts.sans,
        textTransform: "uppercase",
        letterSpacing: "0.5px",
        marginBottom: 8,
      }}>
        Measurement Probabilities
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {labels.map((label, i) => {
          const prob = probabilities[i];
          const pct = (prob * 100);
          const barWidth = (prob / maxProb) * 100;
          return (
            <div
              key={label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                opacity: prob < 0.001 ? 0.35 : 1,
              }}
            >
              <span
                style={{
                  width: 48,
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
                  position: "relative",
                }}
              >
                <div
                  style={{
                    width: `${barWidth}%`,
                    height: "100%",
                    background: prob > 0.001
                      ? `linear-gradient(90deg, ${colors.accent}, ${colors.accentLight})`
                      : "transparent",
                    borderRadius: 4,
                    transition: "width 0.3s ease",
                  }}
                />
              </div>
              <span
                style={{
                  width: 48,
                  color: prob > 0.001 ? colors.text : colors.textTertiary,
                  fontSize: 12,
                  fontFamily: fonts.mono,
                  textAlign: "right",
                  flexShrink: 0,
                }}
              >
                {pct < 0.1 && pct > 0 ? "<0.1" : pct.toFixed(1)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
