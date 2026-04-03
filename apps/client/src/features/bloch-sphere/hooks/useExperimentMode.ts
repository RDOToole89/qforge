import { useState, useEffect, useMemo } from "react";
import type { BlochVisualizerData, StoredResultEntry } from "../../../lib/types";
import type { ProbeStateConfig, ExperimentalDataEntry } from "../types";
import { listResults, getBlochData } from "../../../lib/api";
import {
  blochDataToStateCfg,
  blochDataToAllQubits,
  blochDataToPairCfg,
  blochDataToFingerprints,
  getQubitPairs,
} from "../experimentAdapter";

export interface UseExperimentModeReturn {
  mode: "builtin" | "experiment";
  setMode: (m: "builtin" | "experiment") => void;
  storedResults: StoredResultEntry[];
  selectedResult: string | null;
  setSelectedResult: (v: string | null) => void;
  blochData: BlochVisualizerData | null;
  setBlochData: (v: BlochVisualizerData | null) => void;
  expLoading: boolean;
  expError: string | null;
  setExpError: (v: string | null) => void;
  selectedQubit: number | "all";
  setSelectedQubit: (v: number | "all") => void;
  selectedPair: [number, number];
  setSelectedPair: (v: [number, number]) => void;
  /** Computed: state config for the active bloch data */
  expStateCfg: ProbeStateConfig | null;
  /** Computed: all qubit positions when selectedQubit === "all" */
  expAllQubits: Array<{ bloch: { rx: number; ry: number; rz: number }; color: string; label: string }> | undefined;
  /** Computed: pair correlator data */
  expPairData: { stateCfg: ProbeStateConfig; correlators: import("../types").CorrelatorSignature; mutualInfo: number } | null;
  /** Computed: fingerprint data for FingerprintViewer */
  expFingerprints: ExperimentalDataEntry[];
  /** Computed: available qubit pairs */
  expQubitPairs: [number, number][];
  /** The active bloch data (may be overridden by sweep) */
  activeBloch: BlochVisualizerData | null;
  setActiveBloch: (v: BlochVisualizerData | null) => void;
}

export function useExperimentMode(
  /** The sweep snapshot, if available, to override blochData */
  sweepSnapshot: BlochVisualizerData | null,
  hasSweep: boolean,
): UseExperimentModeReturn {
  const [mode, setMode] = useState<"builtin" | "experiment">("builtin");
  const [storedResults, setStoredResults] = useState<StoredResultEntry[]>([]);
  const [selectedResult, setSelectedResult] = useState<string | null>(null);
  const [blochData, setBlochData] = useState<BlochVisualizerData | null>(null);
  const [expLoading, setExpLoading] = useState(false);
  const [expError, setExpError] = useState<string | null>(null);
  const [selectedQubit, setSelectedQubit] = useState<number | "all">(0);
  const [selectedPair, setSelectedPair] = useState<[number, number]>([0, 1]);

  // Fetch stored results when switching to experiment mode
  useEffect(() => {
    if (mode === "experiment" && storedResults.length === 0) {
      listResults(100, 0)
        .then(setStoredResults)
        .catch(() => setStoredResults([]));
    }
  }, [mode]);

  // Fetch Bloch data when a result is selected
  useEffect(() => {
    if (!selectedResult) { setBlochData(null); return; }
    setExpLoading(true);
    setExpError(null);
    getBlochData(selectedResult)
      .then((data) => {
        setBlochData(data);
        setSelectedQubit(0);
        if (data.num_qubits >= 2) setSelectedPair([0, 1]);
      })
      .catch((e: Error) => setExpError(e.message))
      .finally(() => setExpLoading(false));
  }, [selectedResult]);

  // Active Bloch data: sweep-interpolated snapshot or single result
  const _activeBloch = hasSweep ? sweepSnapshot : blochData;

  // Experiment-mode derived data
  const expStateCfg = useMemo(() => {
    if (!_activeBloch) return null;
    if (selectedQubit === "all") return blochDataToStateCfg(_activeBloch, 0);
    return blochDataToStateCfg(_activeBloch, selectedQubit);
  }, [_activeBloch, selectedQubit]);

  const expAllQubits = useMemo(() => {
    if (!_activeBloch || selectedQubit !== "all") return undefined;
    return blochDataToAllQubits(_activeBloch);
  }, [_activeBloch, selectedQubit]);

  const expPairData = useMemo(() => {
    if (!_activeBloch) return null;
    return blochDataToPairCfg(_activeBloch, selectedPair[0], selectedPair[1]);
  }, [_activeBloch, selectedPair]);

  const expFingerprints = useMemo(() => {
    if (!_activeBloch) return [];
    return blochDataToFingerprints(_activeBloch);
  }, [_activeBloch]);

  const expQubitPairs = useMemo(() => {
    if (!_activeBloch) return [];
    return getQubitPairs(_activeBloch);
  }, [_activeBloch]);

  return {
    mode, setMode,
    storedResults,
    selectedResult, setSelectedResult,
    blochData, setBlochData,
    expLoading,
    expError, setExpError,
    selectedQubit, setSelectedQubit,
    selectedPair, setSelectedPair,
    expStateCfg,
    expAllQubits,
    expPairData,
    expFingerprints,
    expQubitPairs,
    activeBloch: _activeBloch,
    setActiveBloch: setBlochData,
  };
}
