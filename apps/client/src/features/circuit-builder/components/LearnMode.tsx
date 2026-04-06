"use dom";

import { MODULES, LESSONS } from "../data/lessonContent";
import { useLearnProgress } from "../hooks/useLearnProgress";
import LessonView from "./LessonView";
import { colors, fonts } from "../styles";

interface LearnModeProps {
  onClose: () => void;
}

export default function LearnMode({ onClose }: LearnModeProps) {
  const {
    progress,
    completeLesson,
    setCurrentLesson,
    setCurrentModule,
    isModuleUnlocked,
    isLessonUnlocked,
    getModuleProgress,
  } = useLearnProgress();

  const currentLesson = progress.currentLesson
    ? LESSONS.find((l) => l.id === progress.currentLesson)
    : null;

  // Get lessons for the current module view
  const currentModuleLessons = LESSONS.filter((l) => l.module === progress.currentModule);
  const currentLessonIndex = currentLesson
    ? currentModuleLessons.findIndex((l) => l.id === currentLesson.id)
    : -1;

  const handleStartLesson = (lessonId: string) => {
    if (isLessonUnlocked(lessonId)) {
      setCurrentLesson(lessonId);
    }
  };

  const handleCompleteLesson = () => {
    if (!currentLesson) return;
    completeLesson(currentLesson.id);

    // Auto-advance to next lesson in module
    const nextIndex = currentLessonIndex + 1;
    if (nextIndex < currentModuleLessons.length) {
      setCurrentLesson(currentModuleLessons[nextIndex].id);
    } else {
      // Module complete — go back to module selector
      setCurrentLesson(null);
    }
  };

  const handleBack = () => {
    if (currentLesson) {
      setCurrentLesson(null);
    } else {
      onClose();
    }
  };

  // If a lesson is active, show the lesson view
  if (currentLesson) {
    return (
      <div style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 56,
        zIndex: 9500,
        background: colors.bg,
        display: "flex",
        flexDirection: "column",
      }}>
        {/* Top bar */}
        <div style={{
          padding: "10px 20px",
          borderBottom: `1px solid ${colors.border}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: colors.surface,
        }}>
          <button onClick={handleBack} style={backBtnStyle}>
            {"\u2190"} Modules
          </button>
          <div style={{
            fontSize: 14,
            fontWeight: 600,
            color: colors.text,
            fontFamily: fonts.sans,
          }}>
            {MODULES.find((m) => m.id === currentLesson.module)?.title}
          </div>
          <button onClick={onClose} style={closeBtnStyle}>
            {"\u2715"}
          </button>
        </div>

        {/* Lesson content */}
        <div style={{ flex: 1, minHeight: 0 }}>
          <LessonView
            lesson={currentLesson}
            onComplete={handleCompleteLesson}
            onBack={handleBack}
            lessonIndex={currentLessonIndex}
            totalLessons={currentModuleLessons.length}
          />
        </div>

        {/* Module progress dots */}
        <div style={{
          padding: "8px 20px",
          borderTop: `1px solid ${colors.border}`,
          display: "flex",
          justifyContent: "center",
          gap: 6,
          background: colors.surface,
        }}>
          {currentModuleLessons.map((l, i) => (
            <div
              key={l.id}
              onClick={() => isLessonUnlocked(l.id) && setCurrentLesson(l.id)}
              style={{
                width: l.id === currentLesson.id ? 20 : 8,
                height: 8,
                borderRadius: 4,
                background: progress.completedLessons.includes(l.id)
                  ? colors.success
                  : l.id === currentLesson.id
                    ? colors.accent
                    : isLessonUnlocked(l.id)
                      ? colors.border
                      : `${colors.border}50`,
                cursor: isLessonUnlocked(l.id) ? "pointer" : "default",
                transition: "all 0.2s ease",
              }}
              title={l.title}
            />
          ))}
        </div>
      </div>
    );
  }

  // Module selector view
  return (
    <div style={{
      position: "fixed",
      inset: 0,
      zIndex: 9500,
      background: "rgba(0,0,0,0.85)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div style={{
        background: colors.bg,
        borderRadius: 16,
        border: `1px solid ${colors.border}`,
        width: "min(90vw, 680px)",
        maxHeight: "90vh",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        boxShadow: "0 24px 80px rgba(0,0,0,0.6)",
      }}>
        {/* Header */}
        <div style={{
          padding: "20px 24px",
          borderBottom: `1px solid ${colors.border}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}>
          <div>
            <h2 style={{
              margin: 0,
              fontSize: 22,
              fontWeight: 700,
              color: colors.text,
              fontFamily: fonts.sans,
            }}>
              Quantum Circuit Academy
            </h2>
            <div style={{
              fontSize: 13,
              color: colors.textSecondary,
              marginTop: 4,
              fontFamily: fonts.sans,
            }}>
              Interactive lessons with live Bloch sphere demonstrations
            </div>
          </div>
          <button onClick={onClose} style={closeBtnStyle}>{"\u2715"}</button>
        </div>

        {/* Module grid */}
        <div style={{
          padding: "20px 24px",
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 12,
          overflowY: "auto",
        }}>
          {MODULES.map((mod) => {
            const unlocked = isModuleUnlocked(mod.id);
            const { completed, total } = getModuleProgress(mod.id);
            const isComplete = completed === total && total > 0;

            return (
              <div
                key={mod.id}
                onClick={() => {
                  if (unlocked) {
                    setCurrentModule(mod.id);
                    // Start first incomplete lesson
                    const moduleLessons = LESSONS.filter((l) => l.module === mod.id);
                    const firstIncomplete = moduleLessons.find((l) =>
                      !progress.completedLessons.includes(l.id) && isLessonUnlocked(l.id),
                    );
                    if (firstIncomplete) {
                      setCurrentLesson(firstIncomplete.id);
                    } else if (moduleLessons.length > 0) {
                      setCurrentLesson(moduleLessons[0].id);
                    }
                  }
                }}
                style={{
                  padding: 16,
                  background: unlocked ? colors.surface : colors.card,
                  borderRadius: 12,
                  border: `1px solid ${isComplete ? colors.success : unlocked ? colors.border : `${colors.border}50`}`,
                  cursor: unlocked ? "pointer" : "default",
                  opacity: unlocked ? 1 : 0.5,
                  transition: "all 0.15s ease",
                }}
              >
                <div style={{
                  fontSize: 28,
                  marginBottom: 8,
                }}>
                  {unlocked ? mod.icon : "\uD83D\uDD12"}
                </div>
                <div style={{
                  fontSize: 14,
                  fontWeight: 700,
                  color: colors.text,
                  fontFamily: fonts.sans,
                  marginBottom: 4,
                }}>
                  Module {mod.id}: {mod.title}
                </div>
                <div style={{
                  fontSize: 11,
                  color: colors.textSecondary,
                  fontFamily: fonts.sans,
                  lineHeight: 1.4,
                  marginBottom: 10,
                }}>
                  {mod.description}
                </div>

                {/* Progress */}
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <div style={{
                    flex: 1,
                    height: 4,
                    borderRadius: 2,
                    background: colors.border,
                    overflow: "hidden",
                  }}>
                    <div style={{
                      width: total > 0 ? `${(completed / total) * 100}%` : "0%",
                      height: "100%",
                      background: isComplete ? colors.success : colors.accent,
                      borderRadius: 2,
                    }} />
                  </div>
                  <span style={{
                    fontSize: 10,
                    color: colors.textTertiary,
                    fontFamily: fonts.mono,
                    minWidth: 30,
                  }}>
                    {completed}/{total}
                  </span>
                </div>

                {/* Lesson dots */}
                <div style={{ display: "flex", gap: 4, marginTop: 8 }}>
                  {LESSONS.filter((l) => l.module === mod.id).map((l) => (
                    <div key={l.id} style={{
                      width: 6,
                      height: 6,
                      borderRadius: 3,
                      background: progress.completedLessons.includes(l.id)
                        ? colors.success
                        : unlocked
                          ? colors.border
                          : `${colors.border}50`,
                    }} />
                  ))}
                </div>

                {!unlocked && (
                  <div style={{
                    fontSize: 10,
                    color: colors.textTertiary,
                    marginTop: 6,
                    fontFamily: fonts.sans,
                  }}>
                    Complete {mod.prerequisiteModules.map((p) => `Module ${p}`).join(" & ")} to unlock
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Overall progress */}
        <div style={{
          padding: "12px 24px",
          borderTop: `1px solid ${colors.border}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}>
          <span style={{
            fontSize: 11,
            color: colors.textTertiary,
            fontFamily: fonts.sans,
          }}>
            {progress.completedLessons.length} / {LESSONS.length} lessons completed
          </span>
          <div style={{
            width: 120,
            height: 4,
            borderRadius: 2,
            background: colors.border,
            overflow: "hidden",
          }}>
            <div style={{
              width: `${(progress.completedLessons.length / LESSONS.length) * 100}%`,
              height: "100%",
              background: colors.accent,
              borderRadius: 2,
            }} />
          </div>
        </div>
      </div>
    </div>
  );
}

const backBtnStyle: React.CSSProperties = {
  background: "transparent",
  color: colors.textSecondary,
  border: `1px solid ${colors.border}`,
  borderRadius: 6,
  padding: "6px 12px",
  fontSize: 12,
  fontFamily: fonts.sans,
  cursor: "pointer",
};

const closeBtnStyle: React.CSSProperties = {
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
};
