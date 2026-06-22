/**
 * Circuit simulation hook.
 *
 * The pure (framework-free) simulation math lives in `@/src/lib/quantum` and is
 * re-exported here so existing call sites keep working unchanged. This file only
 * owns the React binding. Do NOT duplicate any quantum formula here.
 */
import { useMemo } from "react";
import type { Circuit } from "../types";

// Re-exported pure quantum math (single source of truth in lib/quantum).
export { simulateCircuit, formatDirac, recognizeState } from "@/src/lib/quantum";

import { simulateCircuit } from "@/src/lib/quantum";

/** React hook: simulate whenever circuit changes */
export function useSimulator(circuit: Circuit) {
  const snapshots = useMemo(() => simulateCircuit(circuit), [circuit]);
  const finalSnapshot = snapshots.length > 0 ? snapshots[snapshots.length - 1] : null;

  return { snapshots, finalSnapshot };
}
