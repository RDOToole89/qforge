import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { DEFAULT_CONFIG } from "../config";
import { buildRuntime, TAU } from "../math";
import type { BlochConfig, RuntimeChannel, ProbeStateConfig } from "../types";

export interface UseBuiltInModeReturn {
  config: BlochConfig;
  setConfig: (c: BlochConfig) => void;
  showConfig: boolean;
  setShowConfig: (v: boolean) => void;
  tab: "single" | "multi" | "ptm" | "data";
  setTab: (t: "single" | "multi" | "ptm" | "data") => void;
  channel: string;
  setChannel: (v: string) => void;
  stateKey: string;
  setStateKey: (v: string) => void;
  strength: number;
  setStrength: (v: number) => void;
  showOrig: boolean;
  setShowOrig: (v: boolean) => void;
  showTrans: boolean;
  setShowTrans: (v: boolean) => void;
  animating: boolean;
  setAnimating: (v: boolean) => void;
  animRef: React.RefObject<number>;
  activeTopo: string;
  setActiveTopo: (v: string) => void;
  viewMode: "full" | "state";
  setViewMode: (v: "full" | "state") => void;
  runtimeCh: Record<string, RuntimeChannel>;
  stateCfg: ProbeStateConfig;
  ch: RuntimeChannel | undefined;
  toggleAnim: () => void;
}

export function useBuiltInMode(): UseBuiltInModeReturn {
  const [config, setConfig] = useState<BlochConfig>(DEFAULT_CONFIG);
  const [showConfig, setShowConfig] = useState(false);
  const [tab, setTab] = useState<"single" | "multi" | "ptm" | "data">("single");
  const [channel, setChannel] = useState("depolarizing");
  const [stateKey, setStateKey] = useState("ghz");
  const [strength, setStrength] = useState(0.3);
  const [showOrig, setShowOrig] = useState(true);
  const [showTrans, setShowTrans] = useState(true);
  const [animating, setAnimating] = useState(false);
  const animRef = useRef<number>(0);
  const [activeTopo, setActiveTopo] = useState("all");
  const [viewMode, setViewMode] = useState<"full" | "state">("full");

  const runtimeCh = useMemo(() => buildRuntime(config.channels), [config.channels]);
  const stateCfg = config.states[stateKey] ?? Object.values(config.states)[0] ?? DEFAULT_CONFIG.states.ghz;
  const ch = runtimeCh[channel];

  // Sync channel selection when config changes
  useEffect(() => {
    if (!runtimeCh[channel]) {
      const f = Object.keys(runtimeCh)[0];
      if (f) setChannel(f);
    }
  }, [runtimeCh, channel]);

  // Sync state key when config changes
  useEffect(() => {
    if (!config.states[stateKey]) {
      const f = Object.keys(config.states)[0];
      if (f) setStateKey(f);
    }
  }, [config.states, stateKey]);

  // Built-in mode animation
  const toggleAnim = useCallback(() => {
    if (animating) {
      setAnimating(false);
      cancelAnimationFrame(animRef.current);
      return;
    }
    setAnimating(true);
    let t = 0;
    const step = () => {
      t += 0.008;
      if (t > 1) t = 0;
      setStrength(0.5 - 0.5 * Math.cos(t * TAU));
      animRef.current = requestAnimationFrame(step);
    };
    animRef.current = requestAnimationFrame(step);
  }, [animating]);

  // Cleanup animation on unmount
  useEffect(() => () => cancelAnimationFrame(animRef.current), []);

  return {
    config, setConfig,
    showConfig, setShowConfig,
    tab, setTab,
    channel, setChannel,
    stateKey, setStateKey,
    strength, setStrength,
    showOrig, setShowOrig,
    showTrans, setShowTrans,
    animating, setAnimating,
    animRef,
    activeTopo, setActiveTopo,
    viewMode, setViewMode,
    runtimeCh, stateCfg, ch,
    toggleAnim,
  };
}
