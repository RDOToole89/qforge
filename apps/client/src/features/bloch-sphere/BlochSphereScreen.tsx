'use dom';

import { useState, useMemo, useCallback } from "react";
import { DEFAULT_CONFIG } from "./config";
import { buildRuntime } from "./math";
import type {
  RuntimeChannel,
  CorrelatorSignature,
  FingerprintEntry,
} from "./types";
import BlochScene from "./components/BlochScene";
import TwoQubitScene from "./components/TwoQubitScene";
import PTMHeatmap from "./components/PTMHeatmap";
import CorrelatorBars from "./components/CorrelatorBars";
import FingerprintViewer from "./components/FingerprintViewer";
import ConfigEditor from "./components/ConfigEditor";

/**
 * Main Bloch Sphere CPTP Visualizer screen.
 * This is a `use dom` component — it renders as HTML on web and in a webview on native.
 */
export default function BlochSphereScreen() {
  const [selectedState, setSelectedState] = useState("ghz");
  const [selectedChannel, setSelectedChannel] = useState("depolarizing");
  const [selectedTopo, setSelectedTopo] = useState("chain");
  const [errorRate, setErrorRate] = useState(0.15);

  const config = DEFAULT_CONFIG;
  const runtimeChannels = useMemo(
    () => buildRuntime(config.channels),
    [config.channels],
  );

  const state = config.states[selectedState];
  const channel: RuntimeChannel | null =
    runtimeChannels[selectedChannel] ?? null;
  const topology = config.topologies[selectedTopo];

  // Compute PTM matrix for display
  const ptmMatrix = useMemo(() => {
    if (!channel) return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
    return channel.ptm(errorRate);
  }, [channel, errorRate]);

  // Compute noisy correlators
  const noisyCorrelators = useMemo((): CorrelatorSignature => {
    const c = state.correlators;
    const p = errorRate;
    // Simple depolarizing-like decay for display
    const decay = 1 - p;
    return {
      zi: (c.zi ?? 0) * decay,
      iz: (c.iz ?? 0) * decay,
      zz: (c.zz ?? 0) * decay * decay,
      xx: (c.xx ?? 0) * decay * decay,
      yy: (c.yy ?? 0) * decay * decay,
      xz: (c.xz ?? 0) * decay * decay,
      zx: (c.zx ?? 0) * decay * decay,
    };
  }, [state, errorRate]);

  // Build fingerprint entries
  const fingerprintEntries = useMemo((): FingerprintEntry[] => {
    const keys: (keyof CorrelatorSignature)[] = [
      "zi", "iz", "zz", "xx", "yy", "xz", "zx",
    ];
    return keys
      .filter(
        (k) =>
          (state.correlators[k] ?? 0) !== 0 ||
          (noisyCorrelators[k] ?? 0) !== 0,
      )
      .map((k) => ({
        label: String(k).toUpperCase(),
        clean: state.correlators[k] ?? 0,
        noisy: noisyCorrelators[k] ?? 0,
      }));
  }, [state, noisyCorrelators]);

  // Build name maps for config editor
  const stateKeys = Object.keys(config.states);
  const stateNames: Record<string, string> = {};
  for (const [k, v] of Object.entries(config.states)) stateNames[k] = v.name;

  const channelKeys = Object.keys(config.channels);
  const channelNames: Record<string, string> = {};
  for (const [k, v] of Object.entries(config.channels))
    channelNames[k] = v.name;

  const topoKeys = Object.keys(config.topologies);
  const topoNames: Record<string, string> = {};
  for (const [k, v] of Object.entries(config.topologies))
    topoNames[k] = v.name;

  return (
    <div
      style={{
        display: "flex",
        width: "100%",
        height: "100vh",
        background: "#0f172a",
        color: "#e2e8f0",
        fontFamily:
          "'SF Mono', 'Fira Code', 'Cascadia Code', monospace",
        overflow: "hidden",
      }}
    >
      {/* Left sidebar: configuration */}
      <div
        style={{
          width: 280,
          minWidth: 280,
          padding: 16,
          borderRight: "1px solid rgba(255,255,255,0.06)",
          overflowY: "auto",
          background: "rgba(0,0,0,0.2)",
        }}
      >
        <div
          style={{
            fontSize: 16,
            fontWeight: 700,
            marginBottom: 16,
            color: "#44ddff",
          }}
        >
          Bloch Sphere CPTP
        </div>
        <ConfigEditor
          stateKeys={stateKeys}
          stateNames={stateNames}
          selectedState={selectedState}
          onStateChange={setSelectedState}
          channelKeys={channelKeys}
          channelNames={channelNames}
          selectedChannel={selectedChannel}
          onChannelChange={setSelectedChannel}
          topoKeys={topoKeys}
          topoNames={topoNames}
          selectedTopo={selectedTopo}
          onTopoChange={setSelectedTopo}
          errorRate={errorRate}
          onErrorRateChange={setErrorRate}
          stateColor={state.color}
          insight={state.insight}
          zBasisSignal={state.zBasisSignal}
        />
      </div>

      {/* Center: 3D visualizations */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          padding: 16,
          gap: 16,
          overflow: "hidden",
        }}
      >
        {/* Title bar */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <span
              style={{
                fontSize: 18,
                fontWeight: 700,
                color: state.color,
              }}
            >
              {state.name}
            </span>
            <span
              style={{
                marginLeft: 12,
                fontSize: 12,
                color: "#64748b",
              }}
            >
              {state.desc}
            </span>
          </div>
          <div style={{ fontSize: 12, color: "#64748b" }}>
            {channel?.name ?? "None"} | p={errorRate.toFixed(2)} |{" "}
            {topology.name}
          </div>
        </div>

        {/* Channel info bar */}
        {channel && (
          <div
            style={{
              display: "flex",
              gap: 16,
              padding: "8px 12px",
              background: "rgba(255,255,255,0.03)",
              borderRadius: 8,
              fontSize: 11,
              color: "#94a3b8",
              flexWrap: "wrap",
            }}
          >
            <div>
              <span style={{ color: "#64748b" }}>Formula: </span>
              {channel.formula}
            </div>
            <div>
              <span style={{ color: "#64748b" }}>Geometry: </span>
              {channel.geometry}
            </div>
            <div>
              <span style={{ color: "#64748b" }}>Kraus: </span>
              <span style={{ fontSize: 10 }}>{channel.kraus}</span>
            </div>
          </div>
        )}

        {/* 3D scenes side by side */}
        <div
          style={{
            flex: 1,
            display: "flex",
            gap: 16,
            minHeight: 0,
          }}
        >
          <div
            style={{
              flex: 1,
              background: config.display.backgroundColor,
              borderRadius: 12,
              overflow: "hidden",
              position: "relative",
            }}
          >
            <div
              style={{
                position: "absolute",
                top: 8,
                left: 12,
                fontSize: 11,
                color: "#64748b",
                zIndex: 1,
              }}
            >
              Single Qubit Bloch Sphere
            </div>
            <BlochScene
              state={state}
              channel={channel}
              errorRate={errorRate}
              pointCount={config.display.pointCount}
            />
          </div>
          <div
            style={{
              flex: 1,
              background: config.display.backgroundColor,
              borderRadius: 12,
              overflow: "hidden",
              position: "relative",
            }}
          >
            <div
              style={{
                position: "absolute",
                top: 8,
                left: 12,
                fontSize: 11,
                color: "#64748b",
                zIndex: 1,
              }}
            >
              2-Qubit Correlator Space (ZI, IZ, ZZ)
            </div>
            <TwoQubitScene
              state={state}
              topology={topology}
              errorRate={errorRate}
            />
          </div>
        </div>
      </div>

      {/* Right sidebar: analysis panels */}
      <div
        style={{
          width: 260,
          minWidth: 260,
          padding: 16,
          borderLeft: "1px solid rgba(255,255,255,0.06)",
          overflowY: "auto",
          background: "rgba(0,0,0,0.2)",
          display: "flex",
          flexDirection: "column",
          gap: 20,
        }}
      >
        <PTMHeatmap
          matrix={ptmMatrix}
          channelName={channel?.name ?? "Identity"}
        />

        <CorrelatorBars
          clean={state.correlators}
          noisy={noisyCorrelators}
          stateColor={state.color}
        />

        <FingerprintViewer
          entries={fingerprintEntries}
          stateColor={state.color}
        />

        {/* Channel insight */}
        {channel && (
          <div
            style={{
              padding: "10px 12px",
              background: "rgba(255,255,255,0.03)",
              borderRadius: 8,
              fontSize: 11,
              color: "#94a3b8",
              lineHeight: 1.6,
              borderLeft: "3px solid #44ddff",
            }}
          >
            <div
              style={{
                fontWeight: 600,
                marginBottom: 4,
                color: "#e2e8f0",
                fontSize: 12,
              }}
            >
              Channel Insight
            </div>
            {channel.insight}
          </div>
        )}
      </div>
    </div>
  );
}
