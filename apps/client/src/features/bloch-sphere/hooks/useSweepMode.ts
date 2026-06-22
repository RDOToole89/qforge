import { useState, useRef, useCallback, useEffect, useMemo } from "react";
import type { BlochVisualizerData, BlochSweepResponse } from "../../../lib/types";
import { runBlochSweep } from "../../../lib/api";
import { interpolateSnapshot } from "../sweepInterpolation";

export interface UseSweepModeReturn {
  sweepData: BlochSweepResponse | null;
  setSweepData: (v: BlochSweepResponse | null) => void;
  sweepLoading: boolean;
  sweepProgress: number;
  setSweepProgress: (v: number) => void;
  sweepAnimating: boolean;
  setSweepAnimating: (v: boolean) => void;
  sweepAnimRef: React.RefObject<number>;
  sweepStateType: string;
  setSweepStateType: (v: string) => void;
  sweepQubits: number;
  setSweepQubits: (v: number) => void;
  sweepNoiseType: string;
  setSweepNoiseType: (v: string) => void;
  sweepSteps: number;
  setSweepSteps: (v: number) => void;
  sweepSnapshot: BlochVisualizerData | null;
  toggleSweepAnim: () => void;
  launchSweep: (callbacks: {
    setSelectedResult: (v: string | null) => void;
    setBlochData: (v: BlochVisualizerData | null) => void;
    setSelectedQubit: (v: number | "all") => void;
    setExpError: (v: string | null) => void;
  }) => void;
}

export function useSweepMode(): UseSweepModeReturn {
  const [sweepData, setSweepData] = useState<BlochSweepResponse | null>(null);
  const [sweepLoading, setSweepLoading] = useState(false);
  const [sweepProgress, setSweepProgress] = useState(0);
  const [sweepAnimating, setSweepAnimating] = useState(false);
  const sweepAnimRef = useRef<number>(0);

  // Sweep config form
  const [sweepStateType, setSweepStateType] = useState("GHZ");
  const [sweepQubits, setSweepQubits] = useState(3);
  const [sweepNoiseType, setSweepNoiseType] = useState("depolarizing");
  const [sweepSteps, setSweepSteps] = useState(8);

  // Sweep: interpolate between snapshots based on sweepProgress (0..1)
  const sweepSnapshot = useMemo(
    (): BlochVisualizerData | null =>
      sweepData ? interpolateSnapshot(sweepData.snapshots, sweepProgress) : null,
    [sweepData, sweepProgress],
  );

  // Sweep animation toggle
  const toggleSweepAnim = useCallback(() => {
    if (sweepAnimating) {
      setSweepAnimating(false);
      cancelAnimationFrame(sweepAnimRef.current);
      return;
    }
    setSweepAnimating(true);
    let t = sweepProgress;
    const step = () => {
      t += 0.003;
      if (t > 1) t = 0;
      setSweepProgress(t);
      sweepAnimRef.current = requestAnimationFrame(step);
    };
    sweepAnimRef.current = requestAnimationFrame(step);
  }, [sweepAnimating, sweepProgress]);

  // Cleanup animation on unmount
  useEffect(() => () => cancelAnimationFrame(sweepAnimRef.current), []);

  // Launch a sweep
  const launchSweep = useCallback((callbacks: {
    setSelectedResult: (v: string | null) => void;
    setBlochData: (v: BlochVisualizerData | null) => void;
    setSelectedQubit: (v: number | "all") => void;
    setExpError: (v: string | null) => void;
  }) => {
    setSweepLoading(true);
    callbacks.setExpError(null);
    // Generate error rates from 0 to 0.5
    const rates = Array.from({ length: sweepSteps }, (_, i) =>
      parseFloat((i / (sweepSteps - 1) * 0.5).toFixed(4))
    );
    runBlochSweep({
      state_type: sweepStateType,
      num_qubits: sweepQubits,
      noise_type: sweepNoiseType,
      error_rates: rates,
      sim_mode: "density_matrix",
      shots: 4096,
      rng_seed: 42,
    })
      .then((data) => {
        setSweepData(data);
        setSweepProgress(0);
        callbacks.setSelectedResult(null);
        callbacks.setBlochData(null);
        callbacks.setSelectedQubit("all");
      })
      .catch((e: Error) => callbacks.setExpError(e.message))
      .finally(() => setSweepLoading(false));
  }, [sweepStateType, sweepQubits, sweepNoiseType, sweepSteps]);

  return {
    sweepData, setSweepData,
    sweepLoading,
    sweepProgress, setSweepProgress,
    sweepAnimating, setSweepAnimating,
    sweepAnimRef,
    sweepStateType, setSweepStateType,
    sweepQubits, setSweepQubits,
    sweepNoiseType, setSweepNoiseType,
    sweepSteps, setSweepSteps,
    sweepSnapshot,
    toggleSweepAnim,
    launchSweep,
  };
}
