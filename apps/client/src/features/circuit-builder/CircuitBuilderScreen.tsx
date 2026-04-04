"use dom";

import { useState, useCallback } from "react";
import { colors, fonts } from "./styles";
import { useCircuit } from "./hooks/useCircuit";
import { useSimulator, formatDirac } from "./hooks/useSimulator";
import { usePlayback } from "./hooks/usePlayback";
import CircuitToolbar from "./components/CircuitToolbar";
import GatePalette from "./components/GatePalette";
import CircuitCanvas from "./components/CircuitCanvas";
import ProbabilityDisplay from "./components/ProbabilityDisplay";
import BlochPlaybackPanel from "./components/BlochPlaybackPanel";
import { getGateDef } from "./data/gateLibrary";
import { CIRCUIT_PRESETS } from "./data/circuitPresets";
import type { GateType, CircuitPreset } from "./types";

export default function CircuitBuilderScreen() {
  const {
    circuit,
    addGate,
    removeGate,
    setParams,
    setControl,
    setNumQubits,
    clear,
    loadPreset,
  } = useCircuit();

  const { snapshots, finalSnapshot } = useSimulator(circuit);
  const playback = usePlayback(snapshots, circuit.numQubits);

  const [selectedGateId, setSelectedGateId] = useState<string | null>(null);
  const [activeGateType, setActiveGateType] = useState<GateType | null>(null);
  const [showGrid, setShowGrid] = useState(false);
  const [activePreset, setActivePreset] = useState<CircuitPreset | null>(null);

  // Toggle gate selection from palette
  const handlePaletteSelect = useCallback((gateType: GateType) => {
    setActiveGateType((prev) => (prev === gateType ? null : gateType));
    setSelectedGateId(null);
  }, []);

  // Click on canvas to place active gate on the clicked qubit wire
  const handleCanvasClick = useCallback(
    (qubit: number) => {
      setSelectedGateId(null);
      if (activeGateType) {
        addGate(activeGateType, qubit);
      }
    },
    [activeGateType, addGate],
  );

  // Click on a placed gate
  const handleGateClick = useCallback((gateId: string) => {
    setSelectedGateId((prev) => (prev === gateId ? null : gateId));
    setActiveGateType(null);
  }, []);

  // Find the selected gate info for the info panel
  const selectedGate = selectedGateId
    ? circuit.moments.flatMap((m) => m.gates).find((g) => g.id === selectedGateId)
    : null;
  const selectedGateDef = selectedGate ? getGateDef(selectedGate.gateType) : null;

  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        background: colors.bg,
        color: colors.text,
        fontFamily: fonts.sans,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* Side-by-side: circuit left, Bloch right */}
      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        {/* Left: circuit content */}
        <div
          style={{
            flex: 1,
            minWidth: 0,
            overflowY: "auto",
            padding: 12,
            display: "flex",
            flexDirection: "column",
            gap: 10,
          }}
        >
          {/* Toolbar */}
          <CircuitToolbar
            numQubits={circuit.numQubits}
            onSetNumQubits={(n) => { setNumQubits(n); setActivePreset(null); }}
            onClear={() => { clear(); setActivePreset(null); }}
            onLoadPreset={(c) => {
              loadPreset(c);
              const preset = CIRCUIT_PRESETS.find((p) => p.circuit === c) ?? null;
              setActivePreset(preset);
            }}
          />

          {/* Gate Palette */}
          <GatePalette
            onGateSelect={handlePaletteSelect}
            activeGate={activeGateType}
            numQubits={circuit.numQubits}
          />

          {/* Active gate hint */}
          {activeGateType && (
            <div
              style={{
                padding: "6px 12px",
                background: colors.accentDim,
                borderRadius: 6,
                color: colors.accentLight,
                fontSize: 12,
                fontFamily: fonts.sans,
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <span style={{ fontWeight: 600 }}>
                {getGateDef(activeGateType).name}
              </span>
              <span style={{ color: colors.textSecondary }}>
                Click on a qubit wire to place, or drag and drop onto a wire. Click gate again to deselect.
              </span>
            </div>
          )}

          {/* Circuit Canvas */}
          <div style={{ position: "relative" }}>
            <CircuitCanvas
              circuit={circuit}
              selectedGateId={selectedGateId}
              onGateClick={handleGateClick}
              onGateDoubleClick={undefined}
              onCanvasClick={handleCanvasClick}
              onDrop={(gateType, qubit) => {
                addGate(gateType as GateType, qubit);
              }}
              showGrid={showGrid}
            />
            {/* Grid toggle */}
            <button
              onClick={() => setShowGrid((v) => !v)}
              title={showGrid ? "Hide moment grid" : "Show moment grid"}
              style={{
                position: "absolute",
                top: 6,
                right: 6,
                width: 28,
                height: 28,
                borderRadius: 6,
                border: `1px solid ${showGrid ? colors.accent : colors.border}`,
                background: showGrid ? colors.accentDim : colors.card,
                color: showGrid ? colors.accentLight : colors.textTertiary,
                fontFamily: fonts.mono,
                fontSize: 14,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              #
            </button>
          </div>

          {/* Gate Info Panel (when a placed gate is selected) */}
          {selectedGate && selectedGateDef && (
            <div
              style={{
                padding: 14,
                background: colors.surface,
                borderRadius: 8,
                border: `1px solid ${selectedGateDef.color}40`,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 8,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span
                    style={{
                      background: `${selectedGateDef.color}20`,
                      color: selectedGateDef.color,
                      padding: "2px 8px",
                      borderRadius: 4,
                      fontFamily: fonts.mono,
                      fontSize: 13,
                      fontWeight: 700,
                    }}
                  >
                    {selectedGateDef.label}
                  </span>
                  <span style={{ fontSize: 14, fontWeight: 600 }}>
                    {selectedGateDef.name}
                  </span>
                </div>
                <button
                  onClick={() => {
                    removeGate(selectedGate.id);
                    setSelectedGateId(null);
                  }}
                  style={{
                    background: `${colors.danger}20`,
                    color: colors.danger,
                    border: "none",
                    borderRadius: 4,
                    padding: "4px 10px",
                    fontSize: 11,
                    fontFamily: fonts.sans,
                    cursor: "pointer",
                  }}
                >
                  Remove
                </button>
              </div>

              <p
                style={{
                  color: colors.textSecondary,
                  fontSize: 13,
                  lineHeight: 1.5,
                  margin: "0 0 8px",
                }}
              >
                {selectedGateDef.description}
              </p>

              {/* Qubits acting on */}
              <div style={{ fontSize: 12, color: colors.textTertiary }}>
                Acting on: {selectedGate.qubits.map((q) => `q${q}`).join(", ")}
                {selectedGateDef.numQubits >= 2 && (
                  <span style={{ marginLeft: 8 }}>
                    (control: q{selectedGate.qubits[0]}, target: q
                    {selectedGate.qubits[selectedGate.qubits.length - 1]})
                  </span>
                )}
              </div>

              {/* Parameter slider for parametric gates */}
              {selectedGateDef.parametric && (
                <div style={{ marginTop: 10 }}>
                  <label
                    style={{
                      fontSize: 12,
                      color: colors.textSecondary,
                      display: "block",
                      marginBottom: 4,
                    }}
                  >
                    {selectedGateDef.paramLabels?.[0] ?? "\u03b8"} ={" "}
                    <span style={{ fontFamily: fonts.mono, color: colors.text }}>
                      {((selectedGate.params?.[0] ?? Math.PI / 2) / Math.PI).toFixed(2)}\u03c0
                    </span>
                  </label>
                  <input
                    type="range"
                    min={0}
                    max={2 * Math.PI}
                    step={0.01}
                    value={selectedGate.params?.[0] ?? Math.PI / 2}
                    onChange={(e) =>
                      setParams(selectedGate.id, [parseFloat(e.target.value)])
                    }
                    style={{ width: "100%", accentColor: selectedGateDef.color }}
                  />
                </div>
              )}

              {/* Control qubit selector for multi-qubit gates */}
              {selectedGateDef.numQubits >= 2 && selectedGateDef.type !== "CZ" && selectedGateDef.type !== "SWAP" && (
                <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 8 }}>
                  <label style={{ fontSize: 12, color: colors.textSecondary }}>
                    Control qubit:
                  </label>
                  <select
                    value={selectedGate.qubits[0]}
                    onChange={(e) =>
                      setControl(selectedGate.id, Number(e.target.value))
                    }
                    style={{
                      background: colors.card,
                      color: colors.text,
                      border: `1px solid ${colors.border}`,
                      borderRadius: 4,
                      padding: "2px 6px",
                      fontSize: 12,
                      fontFamily: fonts.mono,
                    }}
                  >
                    {Array.from({ length: circuit.numQubits }, (_, i) => i)
                      .filter((i) => i !== selectedGate.qubits[selectedGate.qubits.length - 1])
                      .map((i) => (
                        <option key={i} value={i}>
                          q{i}
                        </option>
                      ))}
                  </select>
                </div>
              )}

              {/* Glossary link */}
              {selectedGateDef.glossaryTermId && (
                <div style={{ marginTop: 10 }}>
                  <span
                    style={{
                      fontSize: 11,
                      color: colors.accentLight,
                      cursor: "pointer",
                      borderBottom: `1px dashed ${colors.accentLight}`,
                    }}
                  >
                    Learn more in Glossary {"\u2192"} {selectedGateDef.name}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* State Evolution Narrative */}
          {snapshots.length > 1 && (
            <div
              style={{
                padding: 12,
                background: colors.surface,
                borderRadius: 8,
                border: `1px solid ${colors.border}`,
              }}
            >
              <div
                style={{
                  color: colors.textSecondary,
                  fontSize: 11,
                  fontWeight: 600,
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                  marginBottom: 8,
                }}
              >
                State Evolution
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {snapshots.map((snap, i) => {
                  if (i === 0) return null; // skip initial |0...0>
                  const moment = circuit.moments[i - 1];
                  const gateDescs = moment.gates
                    .map((g) => {
                      const def = getGateDef(g.gateType);
                      const qStr = g.qubits.map((q) => `q${q}`).join(",");
                      return `${def.label}(${qStr})`;
                    })
                    .join(", ");

                  return (
                    <div key={i} style={{ paddingLeft: 12, borderLeft: `2px solid ${colors.accent}40` }}>
                      <div
                        style={{
                          fontSize: 12,
                          color: colors.accentLight,
                          fontWeight: 600,
                          marginBottom: 2,
                        }}
                      >
                        Step {i}: {gateDescs}
                      </div>
                      <div
                        style={{
                          fontSize: 13,
                          color: colors.text,
                          fontFamily: fonts.mono,
                        }}
                      >
                        {formatDirac(snap)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Probability Display */}
          <ProbabilityDisplay snapshot={finalSnapshot} />

          {/* Preset Info Panel */}
          {activePreset && (
            <div
              style={{
                padding: 16,
                background: colors.surface,
                borderRadius: 8,
                border: `1px solid ${colors.accent}30`,
              }}
            >
              {/* Title + description */}
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                marginBottom: 10,
              }}>
                <span style={{
                  background: `${colors.accent}20`,
                  color: colors.accentLight,
                  padding: "3px 10px",
                  borderRadius: 4,
                  fontFamily: fonts.mono,
                  fontSize: 12,
                  fontWeight: 700,
                }}>
                  {activePreset.name}
                </span>
                <span style={{
                  fontSize: 11,
                  color: colors.textTertiary,
                  fontFamily: fonts.sans,
                }}>
                  {activePreset.learns}
                </span>
              </div>

              <p style={{
                color: colors.textSecondary,
                fontSize: 13,
                lineHeight: 1.6,
                margin: "0 0 12px",
                fontFamily: fonts.sans,
              }}>
                {activePreset.description}
              </p>

              {/* Step-by-step explanation */}
              {activePreset.steps && activePreset.steps.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <div style={{
                    color: colors.textSecondary,
                    fontSize: 11,
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.5px",
                    marginBottom: 8,
                    fontFamily: fonts.sans,
                  }}>
                    Step-by-Step
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {activePreset.steps.map((step, i) => (
                      <div key={i} style={{
                        display: "flex",
                        gap: 8,
                        fontSize: 12,
                        lineHeight: 1.5,
                        fontFamily: fonts.sans,
                      }}>
                        <span style={{
                          color: colors.accentLight,
                          fontWeight: 700,
                          fontFamily: fonts.mono,
                          fontSize: 11,
                          minWidth: 18,
                          flexShrink: 0,
                          marginTop: 1,
                        }}>
                          {i + 1}.
                        </span>
                        <span style={{ color: colors.text }}>
                          {step}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Applications */}
              {activePreset.applications && activePreset.applications.length > 0 && (
                <div>
                  <div style={{
                    color: colors.textSecondary,
                    fontSize: 11,
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.5px",
                    marginBottom: 8,
                    fontFamily: fonts.sans,
                  }}>
                    Real-World Applications
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    {activePreset.applications.map((app, i) => (
                      <div key={i} style={{
                        display: "flex",
                        gap: 8,
                        fontSize: 12,
                        lineHeight: 1.5,
                        fontFamily: fonts.sans,
                      }}>
                        <span style={{ color: colors.accentLight, flexShrink: 0 }}>{"\u2022"}</span>
                        <span style={{ color: colors.textSecondary }}>{app}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: Bloch sphere playback panel */}
        <div style={{ width: 320, flexShrink: 0 }}>
          <BlochPlaybackPanel
            playback={playback}
            numQubits={circuit.numQubits}
          />
        </div>
      </div>
    </div>
  );
}
