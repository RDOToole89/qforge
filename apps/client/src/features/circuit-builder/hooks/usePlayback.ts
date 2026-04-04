import { useState, useRef, useCallback, useEffect } from "react";
import type { SimSnapshot } from "../types";
import { stateVectorToBloch, correlationMatrix, pairConcurrence } from "@/src/features/bloch-sphere/math";
import type { BlochDot } from "@/src/features/bloch-sphere/data/stateBlochConfigs";

/** Fixed color palette for qubit dots */
const QUBIT_COLORS = ["#818cf8", "#f472b6", "#34d399", "#fb923c", "#38bdf8", "#a78bfa"];

/** Duration of one step in ms at speed=1 */
const STEP_DURATION_MS = 800;

export type PlaybackStatus = "idle" | "playing" | "paused";

/** Correlation data for the current playback frame */
export interface CorrelationData {
  /** ΔCov matrix: ⟨ZiZj⟩ - ⟨Zi⟩⟨Zj⟩, size numQubits × numQubits */
  deltaCov: number[][];
  /** Pairwise concurrence, size numQubits × numQubits (symmetric, diagonal = 0) */
  concurrences: number[][];
}

export interface PlaybackState {
  snapshotIndex: number;
  t: number;
  status: PlaybackStatus;
  speed: number;
  dots: BlochDot[];
  correlations: CorrelationData | null;
}

export interface UsePlaybackReturn {
  state: PlaybackState;
  play: () => void;
  pause: () => void;
  stepForward: () => void;
  stepBack: () => void;
  setSpeed: (s: number) => void;
  reset: () => void;
  totalSnapshots: number;
}

function computeFrame(
  snapshots: SimSnapshot[],
  numQubits: number,
  snapshotIndex: number,
  t: number,
): { dots: BlochDot[]; correlations: CorrelationData | null } {
  const svA = snapshots[snapshotIndex]?.stateVector;
  if (!svA) return { dots: [], correlations: null };

  const hasNext = snapshotIndex + 1 < snapshots.length;
  const svB = hasNext ? snapshots[snapshotIndex + 1].stateVector : null;

  const dots: BlochDot[] = [];
  for (let q = 0; q < numQubits; q++) {
    const a = stateVectorToBloch(svA, q, numQubits);
    let rx = a.rx, ry = a.ry, rz = a.rz;

    if (svB && t > 0) {
      const b = stateVectorToBloch(svB, q, numQubits);
      rx += (b.rx - rx) * t;
      ry += (b.ry - ry) * t;
      rz += (b.rz - rz) * t;
    }

    dots.push({
      rx, ry, rz,
      color: QUBIT_COLORS[q % QUBIT_COLORS.length],
      label: `q${q}`,
    });
  }

  // Compute correlation data from the current (non-interpolated) state vector
  // Use the snapshot we're closest to for clean values
  const sv = (t > 0.5 && svB) ? svB : svA;
  let correlations: CorrelationData | null = null;
  if (numQubits >= 2) {
    const deltaCov = correlationMatrix(sv, numQubits);
    const concurrences: number[][] = [];
    for (let i = 0; i < numQubits; i++) {
      const row: number[] = [];
      for (let j = 0; j < numQubits; j++) {
        if (i === j) {
          row.push(0);
        } else if (j < i) {
          row.push(concurrences[j][i]); // symmetric
        } else {
          row.push(pairConcurrence(sv, i, j, numQubits));
        }
      }
      concurrences.push(row);
    }
    correlations = { deltaCov, concurrences };
  }

  return { dots, correlations };
}

export function usePlayback(
  snapshots: SimSnapshot[],
  numQubits: number,
): UsePlaybackReturn {
  const [snapshotIndex, setSnapshotIndex] = useState(0);
  const [t, setT] = useState(0);
  const [status, setStatus] = useState<PlaybackStatus>("idle");
  const [speed, setSpeedState] = useState(1);

  const statusRef = useRef(status);
  useEffect(() => { statusRef.current = status; }, [status]);
  const speedRef = useRef(speed);
  useEffect(() => { speedRef.current = speed; }, [speed]);
  const snapshotIndexRef = useRef(snapshotIndex);
  useEffect(() => { snapshotIndexRef.current = snapshotIndex; }, [snapshotIndex]);
  const tRef = useRef(t);
  useEffect(() => { tRef.current = t; }, [t]);

  const frameRef = useRef(0);
  const lastTimeRef = useRef(0);

  // Reset when circuit changes
  useEffect(() => {
    setSnapshotIndex(0);
    setT(0);
    setStatus("idle");
  }, [snapshots.length, numQubits]);

  const { dots, correlations } = computeFrame(snapshots, numQubits, snapshotIndex, t);

  const startAnimation = useCallback(() => {
    lastTimeRef.current = performance.now();

    const tick = (now: number) => {
      if (statusRef.current !== "playing") return;

      const dt = now - lastTimeRef.current;
      lastTimeRef.current = now;

      const advance = (dt / STEP_DURATION_MS) * speedRef.current;
      let newT = tRef.current + advance;
      let newIdx = snapshotIndexRef.current;

      while (newT >= 1) {
        newT -= 1;
        newIdx += 1;
      }

      // Reached the end
      if (newIdx >= snapshots.length - 1) {
        setSnapshotIndex(snapshots.length - 1);
        setT(0);
        setStatus("idle");
        return;
      }

      setSnapshotIndex(newIdx);
      setT(newT);
      frameRef.current = requestAnimationFrame(tick);
    };

    frameRef.current = requestAnimationFrame(tick);
  }, [snapshots.length]);

  const play = useCallback(() => {
    if (snapshots.length <= 1) return;
    // If at end, restart from beginning
    if (snapshotIndexRef.current >= snapshots.length - 1) {
      setSnapshotIndex(0);
      setT(0);
    }
    setStatus("playing");
  }, [snapshots.length]);

  // Start/stop animation loop based on status
  useEffect(() => {
    if (status === "playing") {
      startAnimation();
    } else {
      cancelAnimationFrame(frameRef.current);
    }
    return () => cancelAnimationFrame(frameRef.current);
  }, [status, startAnimation]);

  const pause = useCallback(() => setStatus("paused"), []);

  const stepForward = useCallback(() => {
    setStatus("paused");
    setT(0);
    setSnapshotIndex((i) => Math.min(i + 1, snapshots.length - 1));
  }, [snapshots.length]);

  const stepBack = useCallback(() => {
    setStatus("paused");
    setT(0);
    setSnapshotIndex((i) => Math.max(i - 1, 0));
  }, []);

  const setSpeed = useCallback((s: number) => setSpeedState(s), []);

  const reset = useCallback(() => {
    setStatus("idle");
    setSnapshotIndex(0);
    setT(0);
  }, []);

  return {
    state: { snapshotIndex, t, status, speed, dots, correlations },
    play,
    pause,
    stepForward,
    stepBack,
    setSpeed,
    reset,
    totalSnapshots: snapshots.length,
  };
}
