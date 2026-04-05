import { useState, useRef, useCallback, useEffect } from "react";
import type { SimSnapshot } from "../types";
import { stateVectorToBloch, correlationMatrix, pairConcurrence, multipartiteTangle, oneTangle } from "@/src/features/bloch-sphere/math";
import type { BlochDot } from "@/src/features/bloch-sphere/data/stateBlochConfigs";

/** Fixed color palette for qubit dots */
const QUBIT_COLORS = ["#818cf8", "#f472b6", "#34d399", "#fb923c", "#38bdf8", "#a78bfa"];

export type InterpolationMode = "direct" | "ideal";

/**
 * Spherical linear interpolation (slerp) for Bloch vectors.
 * Follows the great circle arc on the sphere surface.
 */
function slerp(
  a: { rx: number; ry: number; rz: number },
  b: { rx: number; ry: number; rz: number },
  t: number,
): { rx: number; ry: number; rz: number } {
  const lenA = Math.sqrt(a.rx * a.rx + a.ry * a.ry + a.rz * a.rz);
  const lenB = Math.sqrt(b.rx * b.rx + b.ry * b.ry + b.rz * b.rz);

  // If either is near the origin (mixed/entangled state), fall back to lerp —
  // slerp can't normalize near-zero vectors without flickering
  if (lenA < 0.3 || lenB < 0.3) {
    return {
      rx: a.rx + (b.rx - a.rx) * t,
      ry: a.ry + (b.ry - a.ry) * t,
      rz: a.rz + (b.rz - a.rz) * t,
    };
  }

  // If start and end are very close, no interpolation needed
  const dx = b.rx - a.rx, dy = b.ry - a.ry, dz = b.rz - a.rz;
  const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
  if (dist < 0.01) return { rx: a.rx, ry: a.ry, rz: a.rz };

  // Normalize to unit sphere
  const ax = a.rx / lenA, ay = a.ry / lenA, az = a.rz / lenA;
  const bx = b.rx / lenB, by = b.ry / lenB, bz = b.rz / lenB;

  // Dot product (cosine of angle between)
  let dot = ax * bx + ay * by + az * bz;
  dot = Math.max(-1, Math.min(1, dot));

  // Nearly parallel — use lerp
  if (dot > 0.9999) {
    return {
      rx: a.rx + (b.rx - a.rx) * t,
      ry: a.ry + (b.ry - a.ry) * t,
      rz: a.rz + (b.rz - a.rz) * t,
    };
  }

  // Nearly antipodal (opposite directions) — slerp is undefined,
  // choose a perpendicular great circle through a fixed axis
  if (dot < -0.9999) {
    // Find a perpendicular vector to create a detour
    let px = 0, py = 0, pz = 0;
    if (Math.abs(ax) < 0.9) { px = 1; } else { py = 1; }
    // Cross product a × p to get perpendicular direction
    const cx = ay * pz - az * py;
    const cy = az * px - ax * pz;
    const cz = ax * py - ay * px;
    const clen = Math.sqrt(cx * cx + cy * cy + cz * cz);
    const nx = cx / clen, ny = cy / clen, nz = cz / clen;
    // Go through the perpendicular midpoint
    const angle = Math.PI * t;
    const cosA = Math.cos(angle), sinA = Math.sin(angle);
    const len = lenA + (lenB - lenA) * t;
    return {
      rx: (ax * cosA + nx * sinA) * len,
      ry: (ay * cosA + ny * sinA) * len,
      rz: (az * cosA + nz * sinA) * len,
    };
  }

  const theta = Math.acos(dot);
  const sinTheta = Math.sin(theta);
  const wA = Math.sin((1 - t) * theta) / sinTheta;
  const wB = Math.sin(t * theta) / sinTheta;

  const len = lenA + (lenB - lenA) * t;

  return {
    rx: (wA * ax + wB * bx) * len,
    ry: (wA * ay + wB * by) * len,
    rz: (wA * az + wB * bz) * len,
  };
}

/** Duration of one step in ms at speed=1 */
const STEP_DURATION_MS = 800;

export type PlaybackStatus = "idle" | "playing" | "paused";

/** Correlation data for the current playback frame */
export interface CorrelationData {
  /** ΔCov matrix: ⟨ZiZj⟩ - ⟨Zi⟩⟨Zj⟩, size numQubits × numQubits */
  deltaCov: number[][];
  /** Pairwise concurrence, size numQubits × numQubits (symmetric, diagonal = 0) */
  concurrences: number[][];
  /** Multipartite tangle: 3-tangle for 3Q, generalized residual tangle for n≥4 */
  tangle: number;
  /** Per-qubit 1-tangle: C²(i|rest) — how entangled each qubit is with everything else */
  oneTangles: number[];
}

export interface PlaybackState {
  snapshotIndex: number;
  t: number;
  status: PlaybackStatus;
  speed: number;
  dots: BlochDot[];
  correlations: CorrelationData | null;
  /** Continuous progress 0..1 across the entire animation */
  progress: number;
}

export interface UsePlaybackReturn {
  state: PlaybackState;
  play: () => void;
  pause: () => void;
  stepForward: () => void;
  stepBack: () => void;
  setSpeed: (s: number) => void;
  reset: () => void;
  seek: (index: number) => void;
  /** Scrub to a continuous position (0..1). Pauses playback. */
  scrubTo: (progress: number) => void;
  /** Snap to the nearest step boundary. Call on mouseUp after scrubbing. */
  snapToStep: () => void;
  totalSnapshots: number;
}

function computeFrame(
  snapshots: SimSnapshot[],
  numQubits: number,
  snapshotIndex: number,
  t: number,
  interpMode: InterpolationMode = "direct",
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
      if (interpMode === "ideal") {
        // Slerp: follow great circle on sphere surface (shows ideal rotation)
        const s = slerp(a, b, t);
        rx = s.rx; ry = s.ry; rz = s.rz;
      } else {
        // Lerp: direct path through interior (shows actual reduced state)
        rx += (b.rx - rx) * t;
        ry += (b.ry - ry) * t;
        rz += (b.rz - rz) * t;
      }
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
    const tangle = multipartiteTangle(sv, numQubits);
    const oneTangles: number[] = [];
    for (let i = 0; i < numQubits; i++) {
      oneTangles.push(oneTangle(sv, i, numQubits));
    }
    correlations = { deltaCov, concurrences, tangle, oneTangles };
  }

  return { dots, correlations };
}

export function usePlayback(
  snapshots: SimSnapshot[],
  numQubits: number,
  interpMode: InterpolationMode = "direct",
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

  // Reset when circuit actually changes (new snapshot count or qubit count)
  const prevLenRef = useRef(snapshots.length);
  const prevQubitsRef = useRef(numQubits);
  useEffect(() => {
    if (snapshots.length !== prevLenRef.current || numQubits !== prevQubitsRef.current) {
      setSnapshotIndex(0);
      setT(0);
      setStatus("idle");
      prevLenRef.current = snapshots.length;
      prevQubitsRef.current = numQubits;
    }
  }, [snapshots.length, numQubits]);

  const { dots, correlations } = computeFrame(snapshots, numQubits, snapshotIndex, t, interpMode);

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

  const seek = useCallback((index: number) => {
    cancelAnimationFrame(frameRef.current);
    setStatus("paused");
    setT(0);
    setSnapshotIndex(index);
  }, []);

  // Continuous scrubbing: progress 0..1 maps to snapshotIndex + t
  const scrubTo = useCallback((progress: number) => {
    cancelAnimationFrame(frameRef.current);
    setStatus("paused");
    const maxIdx = Math.max(snapshots.length - 1, 1);
    const continuous = progress * maxIdx;
    const idx = Math.floor(continuous);
    const frac = continuous - idx;
    setSnapshotIndex(Math.min(idx, snapshots.length - 1));
    setT(idx >= snapshots.length - 1 ? 0 : frac);
  }, [snapshots.length]);

  // Snap to nearest step on release
  const snapToStep = useCallback(() => {
    setT((currentT) => {
      if (currentT > 0.5) {
        setSnapshotIndex((i) => Math.min(i + 1, snapshots.length - 1));
      }
      return 0;
    });
  }, [snapshots.length]);

  // Compute continuous progress
  const maxIdx = Math.max(snapshots.length - 1, 1);
  const progress = (snapshotIndex + t) / maxIdx;

  return {
    state: { snapshotIndex, t, status, speed, dots, correlations, progress },
    play,
    pause,
    stepForward,
    stepBack,
    setSpeed,
    reset,
    seek,
    scrubTo,
    snapToStep,
    totalSnapshots: snapshots.length,
  };
}
