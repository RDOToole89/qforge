import { useState, useCallback } from "react";
import { LESSONS, MODULES } from "../data/lessonContent";

const STORAGE_KEY = "circuit-builder-learn-progress";

export interface LearnProgress {
  completedLessons: string[];
  currentModule: number;
  currentLesson: string | null;
}

const INITIAL: LearnProgress = {
  completedLessons: [],
  currentModule: 1,
  currentLesson: null,
};

function load(): LearnProgress {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return { ...INITIAL, ...JSON.parse(raw) };
  } catch { /* noop */ }
  return INITIAL;
}

function save(progress: LearnProgress) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(progress)); } catch { /* noop */ }
}

export function useLearnProgress() {
  const [progress, setProgress] = useState<LearnProgress>(load);

  const completeLesson = useCallback((lessonId: string) => {
    setProgress((prev) => {
      if (prev.completedLessons.includes(lessonId)) return prev;
      const next = {
        ...prev,
        completedLessons: [...prev.completedLessons, lessonId],
      };
      save(next);
      return next;
    });
  }, []);

  const setCurrentLesson = useCallback((lessonId: string | null) => {
    setProgress((prev) => {
      const next = { ...prev, currentLesson: lessonId };
      save(next);
      return next;
    });
  }, []);

  const setCurrentModule = useCallback((moduleId: number) => {
    setProgress((prev) => {
      const next = { ...prev, currentModule: moduleId, currentLesson: null };
      save(next);
      return next;
    });
  }, []);

  const isModuleUnlocked = useCallback((moduleId: number): boolean => {
    const mod = MODULES.find((m) => m.id === moduleId);
    if (!mod) return false;
    // Check all prerequisite modules are complete
    return mod.prerequisiteModules.every((prereqId) => {
      const prereqLessons = LESSONS.filter((l) => l.module === prereqId);
      return prereqLessons.every((l) => progress.completedLessons.includes(l.id));
    });
  }, [progress.completedLessons]);

  const isLessonUnlocked = useCallback((lessonId: string): boolean => {
    const lesson = LESSONS.find((l) => l.id === lessonId);
    if (!lesson) return false;
    // Module must be unlocked
    if (!isModuleUnlocked(lesson.module)) return false;
    // All prerequisites must be completed
    return lesson.prerequisites.every((prereq) =>
      progress.completedLessons.includes(prereq),
    );
  }, [progress.completedLessons, isModuleUnlocked]);

  const getModuleProgress = useCallback((moduleId: number): { completed: number; total: number } => {
    const moduleLessons = LESSONS.filter((l) => l.module === moduleId);
    const completed = moduleLessons.filter((l) => progress.completedLessons.includes(l.id)).length;
    return { completed, total: moduleLessons.length };
  }, [progress.completedLessons]);

  const resetProgress = useCallback(() => {
    setProgress(INITIAL);
    save(INITIAL);
  }, []);

  return {
    progress,
    completeLesson,
    setCurrentLesson,
    setCurrentModule,
    isModuleUnlocked,
    isLessonUnlocked,
    getModuleProgress,
    resetProgress,
  };
}
