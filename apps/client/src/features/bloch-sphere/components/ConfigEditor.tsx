'use dom';

import React from "react";

interface ConfigEditorProps {
  /** Keys of available states */
  stateKeys: string[];
  /** Display names for states */
  stateNames: Record<string, string>;
  /** Currently selected state key */
  selectedState: string;
  onStateChange: (key: string) => void;

  /** Keys of available channels */
  channelKeys: string[];
  /** Display names for channels */
  channelNames: Record<string, string>;
  /** Currently selected channel key */
  selectedChannel: string;
  onChannelChange: (key: string) => void;

  /** Keys of available topologies */
  topoKeys: string[];
  /** Display names for topologies */
  topoNames: Record<string, string>;
  /** Currently selected topology key */
  selectedTopo: string;
  onTopoChange: (key: string) => void;

  /** Error rate 0-1 */
  errorRate: number;
  onErrorRateChange: (rate: number) => void;

  /** State color for accent */
  stateColor: string;

  /** Insight text for current state */
  insight: string;

  /** Z-basis signal strength label */
  zBasisSignal: string;
}

const selectStyle: React.CSSProperties = {
  width: "100%",
  padding: "6px 8px",
  background: "rgba(255,255,255,0.05)",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: 6,
  color: "#e2e8f0",
  fontSize: 13,
  fontFamily: "monospace",
  outline: "none",
  cursor: "pointer",
};

const labelStyle: React.CSSProperties = {
  color: "#94a3b8",
  fontSize: 11,
  fontWeight: 600,
  textTransform: "uppercase" as const,
  letterSpacing: "0.05em",
  marginBottom: 4,
  display: "block",
};

export default function ConfigEditor({
  stateKeys,
  stateNames,
  selectedState,
  onStateChange,
  channelKeys,
  channelNames,
  selectedChannel,
  onChannelChange,
  topoKeys,
  topoNames,
  selectedTopo,
  onTopoChange,
  errorRate,
  onErrorRateChange,
  stateColor,
  insight,
  zBasisSignal,
}: ConfigEditorProps) {
  return (
    <div style={{ fontFamily: "monospace", fontSize: 13 }}>
      {/* State selector */}
      <div style={{ marginBottom: 16 }}>
        <label style={labelStyle}>Probe State</label>
        <select
          style={{ ...selectStyle, borderColor: stateColor }}
          value={selectedState}
          onChange={(e) => onStateChange(e.target.value)}
        >
          {stateKeys.map((k) => (
            <option key={k} value={k}>
              {stateNames[k]}
            </option>
          ))}
        </select>
      </div>

      {/* Z-basis signal badge */}
      <div style={{ marginBottom: 12 }}>
        <span
          style={{
            display: "inline-block",
            padding: "2px 8px",
            borderRadius: 4,
            fontSize: 10,
            fontWeight: 700,
            textTransform: "uppercase",
            background:
              zBasisSignal === "strong"
                ? "rgba(68, 255, 136, 0.15)"
                : zBasisSignal === "weak"
                  ? "rgba(255, 200, 50, 0.15)"
                  : "rgba(255, 68, 102, 0.15)",
            color:
              zBasisSignal === "strong"
                ? "#44ff88"
                : zBasisSignal === "weak"
                  ? "#ffc832"
                  : "#ff4466",
            border: `1px solid ${
              zBasisSignal === "strong"
                ? "rgba(68, 255, 136, 0.3)"
                : zBasisSignal === "weak"
                  ? "rgba(255, 200, 50, 0.3)"
                  : "rgba(255, 68, 102, 0.3)"
            }`,
          }}
        >
          Z-basis: {zBasisSignal}
        </span>
      </div>

      {/* Insight text */}
      <div
        style={{
          color: "#94a3b8",
          fontSize: 11,
          lineHeight: 1.5,
          marginBottom: 16,
          padding: "8px 10px",
          background: "rgba(255,255,255,0.03)",
          borderRadius: 6,
          borderLeft: `3px solid ${stateColor}`,
        }}
      >
        {insight}
      </div>

      {/* Channel selector */}
      <div style={{ marginBottom: 16 }}>
        <label style={labelStyle}>Noise Channel</label>
        <select
          style={selectStyle}
          value={selectedChannel}
          onChange={(e) => onChannelChange(e.target.value)}
        >
          {channelKeys.map((k) => (
            <option key={k} value={k}>
              {channelNames[k]}
            </option>
          ))}
        </select>
      </div>

      {/* Topology selector */}
      <div style={{ marginBottom: 16 }}>
        <label style={labelStyle}>Topology</label>
        <select
          style={selectStyle}
          value={selectedTopo}
          onChange={(e) => onTopoChange(e.target.value)}
        >
          {topoKeys.map((k) => (
            <option key={k} value={k}>
              {topoNames[k]}
            </option>
          ))}
        </select>
      </div>

      {/* Error rate slider */}
      <div style={{ marginBottom: 8 }}>
        <label style={labelStyle}>
          Error Rate: {(errorRate * 100).toFixed(0)}%
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={errorRate}
          onChange={(e) => onErrorRateChange(parseFloat(e.target.value))}
          style={{
            width: "100%",
            accentColor: stateColor,
            cursor: "pointer",
          }}
        />
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontSize: 9,
            color: "#64748b",
            marginTop: 2,
          }}
        >
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>
    </div>
  );
}
