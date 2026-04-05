"use dom";

import { useMemo, useEffect } from "react";
import UnifiedBlochSphere from "@/src/features/bloch-sphere/components/UnifiedBlochSphere";
import { simulateCircuit } from "../hooks/useSimulator";
import { usePlayback } from "../hooks/usePlayback";
import type { Lesson, LessonSection } from "../data/lessonContent";
import { colors, fonts } from "../styles";

interface LessonViewProps {
  lesson: Lesson;
  onComplete: () => void;
  onBack: () => void;
  lessonIndex: number;
  totalLessons: number;
}

export default function LessonView({ lesson, onComplete, onBack, lessonIndex, totalLessons }: LessonViewProps) {
  const snapshots = useMemo(() => simulateCircuit(lesson.circuit), [lesson.id]);
  const playback = usePlayback(snapshots, lesson.circuit.numQubits, lesson.interpMode ?? "direct");
  const { state, play, pause, stepForward, stepBack, reset } = playback;
  const { dots, snapshotIndex, status, progress } = state;

  // Compute active qubits for the current step
  const activeQubits = useMemo(() => {
    const { snapshotIndex: si, t } = state;
    if (status === "idle" && t === 0 && si === 0) return undefined;
    if (si >= snapshots.length - 1 && t === 0) return undefined;
    const mi = t > 0 ? si : Math.max(0, si - 1);
    const moment = lesson.circuit.moments[mi];
    if (!moment) return undefined;
    return [...new Set(moment.gates.flatMap((g) => g.qubits))];
  }, [state, lesson.circuit.moments, snapshots.length, status]);

  // Auto-play on mount
  useEffect(() => {
    const t = setTimeout(() => play(), 300);
    return () => clearTimeout(t);
  }, [lesson.id]);

  return (
    <div style={{
      display: "flex",
      height: "100%",
      minHeight: 0,
      gap: 0,
    }}>
      {/* Left: Bloch sphere + controls */}
      <div style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        minWidth: 0,
        background: colors.bg,
        borderRight: `1px solid ${colors.border}`,
      }}>
        {/* Sphere */}
        <div style={{ flex: 1, minHeight: 0 }}>
          <UnifiedBlochSphere
            mode="circuit"
            dots={dots}
            zoom={1.3}
            activeQubits={activeQubits}
            stepProgress={state.t}
          />
        </div>

        {/* Transport controls */}
        <div style={{
          padding: "8px 16px",
          borderTop: `1px solid ${colors.border}`,
          display: "flex",
          flexDirection: "column",
          gap: 4,
          alignItems: "center",
        }}>
          {/* Progress bar */}
          <div style={{
            width: "100%",
            height: 4,
            borderRadius: 2,
            background: colors.border,
            overflow: "hidden",
          }}>
            <div style={{
              width: `${progress * 100}%`,
              height: "100%",
              background: colors.accent,
              borderRadius: 2,
            }} />
          </div>

          <div style={{
            fontSize: 10,
            color: colors.textTertiary,
            fontFamily: fonts.mono,
          }}>
            Step {snapshotIndex} / {snapshots.length - 1}
          </div>

          <div style={{ display: "flex", gap: 4 }}>
            <SmallButton onClick={reset} title="Reset">{"\u23EE"}</SmallButton>
            <SmallButton onClick={stepBack} title="Step back">{"\u23EA"}</SmallButton>
            {status === "playing" ? (
              <SmallButton onClick={pause} title="Pause" accent>{"\u23F8"}</SmallButton>
            ) : (
              <SmallButton onClick={play} title="Play" accent>{"\u25B6"}</SmallButton>
            )}
            <SmallButton onClick={stepForward} title="Step forward">{"\u23E9"}</SmallButton>
          </div>
        </div>
      </div>

      {/* Right: Lesson content */}
      <div style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        minWidth: 0,
        overflowY: "auto",
        background: colors.surface,
      }}>
        {/* Header */}
        <div style={{
          padding: "20px 24px 12px",
          borderBottom: `1px solid ${colors.border}`,
        }}>
          <div style={{
            fontSize: 10,
            color: colors.accentLight,
            fontFamily: fonts.sans,
            fontWeight: 600,
            textTransform: "uppercase",
            letterSpacing: "0.5px",
            marginBottom: 4,
          }}>
            Lesson {lessonIndex + 1} of {totalLessons}
          </div>
          <h2 style={{
            margin: 0,
            fontSize: 20,
            fontWeight: 700,
            color: colors.text,
            fontFamily: fonts.sans,
          }}>
            {lesson.title}
          </h2>
          <div style={{
            fontSize: 13,
            color: colors.textSecondary,
            marginTop: 4,
            fontFamily: fonts.sans,
          }}>
            {lesson.subtitle}
          </div>
        </div>

        {/* Content sections */}
        <div style={{
          flex: 1,
          padding: "16px 24px",
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}>
          {lesson.content.map((section, i) => (
            <SectionRenderer key={i} section={section} />
          ))}

          {/* Glossary links */}
          {lesson.glossaryLinks.length > 0 && (
            <div style={{
              marginTop: 8,
              padding: "8px 12px",
              background: colors.card,
              borderRadius: 8,
              display: "flex",
              flexWrap: "wrap",
              gap: 6,
              alignItems: "center",
            }}>
              <span style={{ fontSize: 10, color: colors.textTertiary, fontFamily: fonts.sans }}>
                Glossary:
              </span>
              {lesson.glossaryLinks.map((term) => (
                <span key={term} style={{
                  fontSize: 10,
                  color: colors.accentLight,
                  background: `${colors.accent}15`,
                  padding: "2px 6px",
                  borderRadius: 3,
                  fontFamily: fonts.mono,
                }}>
                  {term}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Navigation */}
        <div style={{
          padding: "12px 24px 16px",
          borderTop: `1px solid ${colors.border}`,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}>
          <button
            onClick={onBack}
            style={{
              background: "transparent",
              color: colors.textSecondary,
              border: `1px solid ${colors.border}`,
              borderRadius: 6,
              padding: "8px 16px",
              fontSize: 12,
              fontFamily: fonts.sans,
              cursor: "pointer",
            }}
          >
            {"\u2190"} Back
          </button>

          <button
            onClick={onComplete}
            style={{
              background: colors.accent,
              color: "#fff",
              border: "none",
              borderRadius: 6,
              padding: "8px 20px",
              fontSize: 13,
              fontWeight: 600,
              fontFamily: fonts.sans,
              cursor: "pointer",
            }}
          >
            {lessonIndex < totalLessons - 1 ? `Next Lesson ${"\u2192"}` : "Complete Module \u2713"}
          </button>
        </div>
      </div>
    </div>
  );
}

function SectionRenderer({ section }: { section: LessonSection }) {
  switch (section.type) {
    case "text":
      return (
        <p style={{
          margin: 0,
          fontSize: 13,
          lineHeight: 1.7,
          color: colors.text,
          fontFamily: fonts.sans,
        }}>
          {section.content}
        </p>
      );
    case "insight":
      return (
        <div style={{
          padding: "10px 14px",
          background: `${colors.accent}10`,
          borderLeft: `3px solid ${colors.accent}`,
          borderRadius: "0 8px 8px 0",
        }}>
          <div style={{
            fontSize: 10,
            fontWeight: 700,
            color: colors.accentLight,
            marginBottom: 4,
            fontFamily: fonts.sans,
            textTransform: "uppercase",
            letterSpacing: "0.5px",
          }}>
            Key Insight
          </div>
          <p style={{
            margin: 0,
            fontSize: 13,
            lineHeight: 1.6,
            color: colors.text,
            fontFamily: fonts.sans,
          }}>
            {section.content}
          </p>
        </div>
      );
    case "watch":
      return (
        <div style={{
          padding: "10px 14px",
          background: `${colors.success}10`,
          borderLeft: `3px solid ${colors.success}`,
          borderRadius: "0 8px 8px 0",
        }}>
          <div style={{
            fontSize: 10,
            fontWeight: 700,
            color: colors.success,
            marginBottom: 4,
            fontFamily: fonts.sans,
            textTransform: "uppercase",
            letterSpacing: "0.5px",
          }}>
            Watch the Sphere
          </div>
          <p style={{
            margin: 0,
            fontSize: 13,
            lineHeight: 1.6,
            color: colors.text,
            fontFamily: fonts.sans,
          }}>
            {section.content}
          </p>
        </div>
      );
    case "formula":
      return (
        <div style={{
          padding: "8px 14px",
          background: colors.card,
          borderRadius: 6,
          fontFamily: fonts.mono,
          fontSize: 13,
          color: colors.accentLight,
          textAlign: "center",
        }}>
          {section.content}
        </div>
      );
    default:
      return null;
  }
}

function SmallButton({ onClick, title, accent, children }: {
  onClick: () => void; title: string; accent?: boolean; children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      title={title}
      style={{
        width: 32,
        height: 28,
        borderRadius: 6,
        border: `1px solid ${accent ? colors.accent : colors.border}`,
        background: accent ? colors.accentDim : colors.card,
        color: accent ? colors.accentLight : colors.text,
        fontSize: 13,
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {children}
    </button>
  );
}
