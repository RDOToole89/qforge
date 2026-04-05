"use dom";

import { useState, useCallback, useMemo, useEffect, useRef } from "react";
import { colors, fonts } from "./styles";
import { useCircuit } from "./hooks/useCircuit";
import { useSimulator, formatDirac, recognizeState } from "./hooks/useSimulator";
import { useNarrative } from "./hooks/useNarrative";
import { usePlayback } from "./hooks/usePlayback";
import CircuitToolbar from "./components/CircuitToolbar";
import GatePalette from "./components/GatePalette";
import CircuitCanvas from "./components/CircuitCanvas";
import ProbabilityDisplay from "./components/ProbabilityDisplay";
import BlochPlaybackPanel from "./components/BlochPlaybackPanel";
import OnboardingOverlay, { OnboardingResetButton } from "./components/OnboardingOverlay";
import type { OnboardingActions } from "./components/OnboardingOverlay";
import { getGateDef } from "./data/gateLibrary";
import { CIRCUIT_PRESETS } from "./data/circuitPresets";
import { IDEAL_STATES, idealStateToSnapshot } from "./data/idealStates";
import { GATE_PREVIEW_CIRCUITS } from "./data/gatePreviewCircuits";
import { simulateCircuit } from "./hooks/useSimulator";
import type { GateType, CircuitPreset, SimSnapshot } from "./types";

export default function CircuitBuilderScreen() {
  const {
    circuit,
    addGate,
    removeGate,
    moveGate,
    setParams,
    setControl,
    setNumQubits,
    clear,
    loadPreset,
  } = useCircuit();

  const { snapshots: circuitSnapshots, finalSnapshot: circuitFinalSnapshot } = useSimulator(circuit);

  // ── Input mode: "circuit" (build gates) or "direct" (ideal state vector) ──
  const [inputMode, setInputMode] = useState<"circuit" | "direct">("circuit");
  const [directStateId, setDirectStateId] = useState<string | null>(null);
  const [customSvText, setCustomSvText] = useState("");
  const [customSvError, setCustomSvError] = useState<string | null>(null);

  // Build snapshot for direct state mode
  const directSnapshot = useMemo((): SimSnapshot | null => {
    if (inputMode !== "direct") return null;

    // Try ideal state first
    if (directStateId) {
      const ideal = IDEAL_STATES.find((s) => s.id === directStateId);
      if (ideal) return idealStateToSnapshot(ideal);
    }

    // Try custom state vector
    if (customSvText.trim()) {
      try {
        const parsed = JSON.parse(customSvText.trim());
        if (!Array.isArray(parsed)) { setCustomSvError("Must be an array"); return null; }
        const dim = parsed.length;
        const n = Math.log2(dim);
        if (!Number.isInteger(n) || n < 1 || n > 6) { setCustomSvError(`Length must be 2^n (2\u201364), got ${dim}`); return null; }
        // Normalize: accept [real, imag] pairs or just real numbers
        const sv = parsed.map((v: number | [number, number]): [number, number] => {
          if (typeof v === "number") return [v, 0];
          if (Array.isArray(v) && v.length === 2) return [v[0], v[1]];
          throw new Error("Each entry must be a number or [real, imag]");
        });
        // Check normalization
        const norm = sv.reduce((s: number, [re, im]: [number, number]) => s + re * re + im * im, 0);
        if (Math.abs(norm - 1) > 0.05) { setCustomSvError(`Not normalized: \u2211|a|² = ${norm.toFixed(4)}, expected 1`); return null; }
        setCustomSvError(null);
        const labels = Array.from({ length: dim }, (_, i) =>
          "|" + i.toString(2).padStart(n, "0") + "\u27E9",
        );
        return {
          stateVector: sv,
          probabilities: sv.map(([re, im]: [number, number]) => re * re + im * im),
          labels,
        };
      } catch (e) {
        setCustomSvError(e instanceof Error ? e.message : "Invalid JSON");
        return null;
      }
    }

    return null;
  }, [inputMode, directStateId, customSvText]);

  const directNumQubits = directSnapshot ? Math.log2(directSnapshot.stateVector.length) : 2;
  const directSnapshots = useMemo(() => directSnapshot ? [directSnapshot] : [], [directSnapshot]);

  const [activeGateType, setActiveGateType] = useState<GateType | null>(null);

  // Gate preview: when a gate is selected in palette, show its effect on the Bloch sphere
  const gatePreview = useMemo(() => {
    if (!activeGateType || inputMode !== "circuit") return null;
    const preview = GATE_PREVIEW_CIRCUITS[activeGateType];
    if (!preview) return null;
    return {
      caption: preview.caption,
      snapshots: simulateCircuit(preview.circuit),
      numQubits: preview.circuit.numQubits,
    };
  }, [activeGateType, inputMode]);

  // Choose which snapshots to feed the playback system
  // Priority: gate preview > direct state > circuit
  const isPreviewActive = gatePreview !== null;
  const snapshots = isPreviewActive
    ? gatePreview!.snapshots
    : inputMode === "direct"
      ? directSnapshots
      : circuitSnapshots;
  const finalSnapshot = isPreviewActive
    ? gatePreview!.snapshots[gatePreview!.snapshots.length - 1]
    : inputMode === "direct"
      ? directSnapshot
      : circuitFinalSnapshot;
  const activeNumQubits = isPreviewActive
    ? gatePreview!.numQubits
    : inputMode === "direct"
      ? directNumQubits
      : circuit.numQubits;

  const playback = usePlayback(snapshots, activeNumQubits);
  const narratives = useNarrative(circuit, circuitSnapshots);

  // Auto-play when gate preview activates — show the transformation
  const prevPreviewRef = useRef<string | null>(null);
  useEffect(() => {
    const currentGate = activeGateType;
    if (currentGate && currentGate !== prevPreviewRef.current) {
      // Small delay so playback hook has the new snapshots
      const t = setTimeout(() => playback.play(), 50);
      prevPreviewRef.current = currentGate;
      return () => clearTimeout(t);
    }
    if (!currentGate) prevPreviewRef.current = null;
  }, [activeGateType, playback]);

  const [selectedGateId, setSelectedGateId] = useState<string | null>(null);
  const [showGrid, setShowGrid] = useState(false);
  const [activePreset, setActivePreset] = useState<CircuitPreset | null>(null);
  const [exportCopied, setExportCopied] = useState(false);
  const [blochFullscreen, setBlochFullscreen] = useState(false);
  const [blochPanelWidth, setBlochPanelWidth] = useState(480);
  const resizingRef = useRef(false);
  const resizeStartRef = useRef({ x: 0, width: 0 });

  // Onboarding actions
  const onboardingActions = useMemo((): OnboardingActions => ({
    loadBellPreset: () => {
      const bellPreset = CIRCUIT_PRESETS.find((p) => p.id === "bell");
      if (bellPreset) {
        loadPreset(bellPreset.circuit);
        setActivePreset(bellPreset);
        setInputMode("circuit");
      }
    },
    playBloch: () => playback.play(),
    resetBloch: () => playback.reset(),
    openFullscreen: () => setBlochFullscreen(true),
    closeFullscreen: () => setBlochFullscreen(false),
  }), [loadPreset, playback]);

  const handleExport = useCallback(() => {
    const json = JSON.stringify(circuit, null, 2);
    navigator.clipboard.writeText(json).then(() => {
      setExportCopied(true);
      setTimeout(() => setExportCopied(false), 2000);
    });
  }, [circuit]);

  // Auto-detect known states and match to presets for educational info
  const detectedPreset = useMemo(() => {
    if (activePreset) return null; // user already selected one manually
    if (!finalSnapshot) return null;
    const stateName = recognizeState(finalSnapshot);
    if (!stateName) return null;

    // Map recognized state names to preset IDs
    const stateToPreset: Record<string, string> = {
      "Bell |\u03A6\u207A\u27E9": "bell",
      "Bell |\u03A6\u207B\u27E9": "bell",
      "Bell |\u03A8\u207A\u27E9": "bell",
      "Bell |\u03A8\u207B\u27E9 (singlet)": "bell_psi_minus",
      "Bell state (|\u03A6\u27E9 variant)": "bell",
      "Bell state (|\u03A8\u27E9 variant)": "bell_psi_minus",
      "GHZ+ state (3Q)": "ghz3",
      "GHZ\u2212 state (3Q)": "ghz3",
      "GHZ\u00B1 state (3Q)": "ghz3",
      "GHZ+ state (4Q)": "ghz4",
      "GHZ\u2212 state (4Q)": "ghz4",
      "GHZ\u00B1 state (4Q)": "ghz4",
      "W state (3Q)": "w_state",
    };

    const presetId = stateToPreset[stateName];
    if (!presetId) return null;

    // Only auto-show if the circuit is simple enough (not a complex circuit
    // that happens to pass through a known state as an intermediate step)
    if (circuit.moments.length > 6) return null;

    return CIRCUIT_PRESETS.find((p) => p.id === presetId) ?? null;
  }, [activePreset, finalSnapshot, circuit.moments.length]);

  // The preset to display: manual selection takes priority, then auto-detected
  const displayPreset = activePreset ?? detectedPreset;

  // Toggle gate selection from palette
  const handlePaletteSelect = useCallback((gateType: GateType) => {
    setActiveGateType((prev) => (prev === gateType ? null : gateType));
    setSelectedGateId(null);
  }, []);

  // Placement popover (error or info)
  const [placementPopover, setPlacementPopover] = useState<{
    message: string; x: number; y: number; kind: "error" | "info";
  } | null>(null);
  useEffect(() => {
    if (!placementPopover) return;
    const t = setTimeout(() => setPlacementPopover(null), placementPopover.kind === "error" ? 4000 : 2500);
    return () => clearTimeout(t);
  }, [placementPopover]);

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{
    gateId: string; x: number; y: number;
  } | null>(null);

  const handleGatePlacementResult = useCallback(
    (result: ReturnType<typeof addGate>, event?: { clientX: number; clientY: number }) => {
      if (!result || !event) return;
      if ("error" in result) {
        setPlacementPopover({ message: result.error, x: event.clientX, y: event.clientY, kind: "error" });
      } else if ("placed" in result && result.placed.qubits.length >= 2) {
        const def = getGateDef(activeGateType!);
        const qLabels = result.placed.qubits.map((q, i) => {
          if (i === result.placed.qubits.length - 1) return `target q${q}`;
          return `control q${q}`;
        }).join(", ");
        setPlacementPopover({
          message: `${def.name} placed: ${qLabels}`,
          x: event.clientX, y: event.clientY, kind: "info",
        });
      }
    },
    [activeGateType],
  );

  // Click on canvas to place active gate on the clicked qubit wire
  const handleCanvasClick = useCallback(
    (qubit: number, event?: React.MouseEvent) => {
      setSelectedGateId(null);
      setContextMenu(null);
      setPlacementPopover(null);
      if (activeGateType) {
        const result = addGate(activeGateType, qubit);
        handleGatePlacementResult(result, event);
      }
    },
    [activeGateType, addGate, handleGatePlacementResult],
  );

  // Right-click context menu on placed gates
  const handleGateContextMenu = useCallback((gateId: string, event: React.MouseEvent) => {
    setContextMenu({ gateId, x: event.clientX, y: event.clientY });
    setSelectedGateId(gateId);
  }, []);

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
      {/* Onboarding overlay (first visit only) */}
      <OnboardingOverlay actions={onboardingActions} />

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
          {/* Mode toggle: Circuit vs Direct State + Tour button */}
          <div data-onboarding="mode-toggle" style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{
              display: "flex",
              gap: 2,
              background: colors.surface,
              borderRadius: 8,
              padding: 3,
              border: `1px solid ${colors.border}`,
            }}>
              {([["circuit", "Circuit Builder"], ["direct", "Direct State"]] as const).map(([mode, label]) => (
                <button
                  key={mode}
                  onClick={() => setInputMode(mode)}
                  style={{
                    background: inputMode === mode ? colors.accent : "transparent",
                    color: inputMode === mode ? "#fff" : colors.textSecondary,
                    border: "none",
                    borderRadius: 6,
                    padding: "6px 16px",
                    fontSize: 12,
                    fontWeight: 600,
                    fontFamily: fonts.sans,
                    cursor: "pointer",
                    transition: "all 0.15s",
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
            <OnboardingResetButton />
          </div>

          {/* ── Circuit mode ── */}
          {inputMode === "circuit" && (
            <>
          {/* Toolbar */}
          <div data-onboarding="toolbar">
            <CircuitToolbar
              numQubits={circuit.numQubits}
              onSetNumQubits={(n) => { setNumQubits(n); setActivePreset(null); }}
              onClear={() => { clear(); setActivePreset(null); }}
              onExport={handleExport}
              activePresetId={activePreset?.id ?? null}
              onLoadPreset={(c) => {
                loadPreset(c);
                const preset = CIRCUIT_PRESETS.find((p) => p.circuit === c) ?? null;
                setActivePreset(preset);
                setActiveGateType(null); // clear gate preview so Bloch shows the circuit
              }}
            />
          </div>

          {/* Gate Palette */}
          <div data-onboarding="palette">
            <GatePalette
              onGateSelect={handlePaletteSelect}
              activeGate={activeGateType}
              numQubits={circuit.numQubits}
            />
          </div>

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
          <div data-onboarding="canvas" style={{ position: "relative" }}>
            <CircuitCanvas
              circuit={circuit}
              selectedGateId={selectedGateId}
              onGateClick={handleGateClick}
              onGateDoubleClick={undefined}
              onGateContextMenu={handleGateContextMenu}
              onGateMove={(gateId, qubit, mi) => {
                moveGate(gateId, qubit, mi);
                setSelectedGateId(null);
              }}
              onCanvasClick={handleCanvasClick}
              onDrop={(gateType, qubit, momentIndex, event) => {
                setActiveGateType(gateType as GateType);
                const result = addGate(gateType as GateType, qubit, momentIndex);
                handleGatePlacementResult(result, event);
                setActiveGateType(null);
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

            {/* Placement popover (error or info) */}
            {placementPopover && (
              <div
                style={{
                  position: "fixed",
                  left: Math.min(placementPopover.x + 12, window.innerWidth - 320),
                  top: Math.max(12, placementPopover.y - 60),
                  maxWidth: 300,
                  padding: "10px 14px",
                  background: colors.bg,
                  border: `1px solid ${placementPopover.kind === "error" ? colors.danger : colors.accent}80`,
                  borderRadius: 10,
                  boxShadow: `0 0 20px ${placementPopover.kind === "error" ? colors.danger : colors.accent}20, 0 8px 24px rgba(0,0,0,0.4)`,
                  zIndex: 9000,
                  animation: "fadeIn 0.15s ease",
                }}
                onClick={() => setPlacementPopover(null)}
              >
                <style>{`@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }`}</style>
                <div style={{
                  fontSize: 12,
                  fontWeight: 600,
                  color: placementPopover.kind === "error" ? colors.danger : colors.accentLight,
                  fontFamily: fonts.sans,
                }}>
                  {placementPopover.kind === "error" ? "Invalid Placement" : placementPopover.message}
                </div>
                {placementPopover.kind === "error" && (
                  <div style={{ fontSize: 12, color: colors.textSecondary, lineHeight: 1.5, fontFamily: fonts.sans, marginTop: 4 }}>
                    {placementPopover.message}
                  </div>
                )}
              </div>
            )}

            {/* Right-click context menu */}
            {contextMenu && (() => {
              const gate = circuit.moments.flatMap((m) => m.gates).find((g) => g.id === contextMenu.gateId);
              if (!gate) return null;
              const def = getGateDef(gate.gateType);
              const MARGIN = 16;
              const menuW = 260;
              const menuX = Math.min(contextMenu.x, window.innerWidth - menuW - MARGIN);
              const menuY = Math.max(MARGIN, Math.min(contextMenu.y, window.innerHeight - 300));

              return (
                <>
                  {/* Backdrop to dismiss */}
                  <div
                    style={{ position: "fixed", inset: 0, zIndex: 8999 }}
                    onClick={() => setContextMenu(null)}
                    onContextMenu={(e) => { e.preventDefault(); setContextMenu(null); }}
                  />
                  <div style={{
                    position: "fixed",
                    left: menuX,
                    top: menuY,
                    width: menuW,
                    background: colors.bg,
                    border: `1px solid ${colors.border}`,
                    borderRadius: 10,
                    boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
                    zIndex: 9000,
                    overflow: "hidden",
                    animation: "fadeIn 0.1s ease",
                  }}>
                    {/* Header */}
                    <div style={{
                      padding: "10px 14px",
                      borderBottom: `1px solid ${colors.border}`,
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                    }}>
                      <span style={{
                        background: `${def.color}20`,
                        color: def.color,
                        padding: "2px 8px",
                        borderRadius: 4,
                        fontFamily: fonts.mono,
                        fontSize: 12,
                        fontWeight: 700,
                      }}>
                        {def.label}
                      </span>
                      <span style={{ fontSize: 12, fontWeight: 600, color: colors.text, fontFamily: fonts.sans }}>
                        {def.name}
                      </span>
                      {def.numQubits >= 2 && (
                        <span style={{ fontSize: 9, color: colors.textTertiary, fontFamily: fonts.mono }}>
                          {def.numQubits}Q
                        </span>
                      )}
                    </div>

                    {/* Description */}
                    <div style={{
                      padding: "8px 14px",
                      fontSize: 11,
                      color: colors.textSecondary,
                      lineHeight: 1.5,
                      fontFamily: fonts.sans,
                      borderBottom: `1px solid ${colors.border}`,
                    }}>
                      {def.description}
                    </div>

                    {/* Qubits info */}
                    <div style={{
                      padding: "6px 14px",
                      fontSize: 11,
                      color: colors.textTertiary,
                      fontFamily: fonts.mono,
                      borderBottom: `1px solid ${colors.border}`,
                    }}>
                      {gate.qubits.map((q, i) => {
                        const role = def.numQubits >= 2
                          ? (i === gate.qubits.length - 1 ? "target" : "control")
                          : "qubit";
                        return `${role}: q${q}`;
                      }).join("  \u00B7  ")}
                    </div>

                    {/* Parameter slider for parametric gates */}
                    {def.parametric && (
                      <div style={{ padding: "8px 14px", borderBottom: `1px solid ${colors.border}` }}>
                        <div style={{ fontSize: 10, color: colors.textSecondary, marginBottom: 4, fontFamily: fonts.sans }}>
                          {def.paramLabels?.[0] ?? "\u03B8"} = {((gate.params?.[0] ?? Math.PI / 2) / Math.PI).toFixed(2)}\u03C0
                        </div>
                        <input
                          type="range"
                          min={0}
                          max={2 * Math.PI}
                          step={0.01}
                          value={gate.params?.[0] ?? Math.PI / 2}
                          onChange={(e) => {
                            setParams(gate.id, [parseFloat(e.target.value)]);
                          }}
                          style={{ width: "100%", accentColor: def.color }}
                        />
                      </div>
                    )}

                    {/* Actions */}
                    <div style={{ padding: "4px 0" }}>
                      {/* Change control qubit (multi-qubit only) */}
                      {def.numQubits >= 2 && def.type !== "CZ" && def.type !== "SWAP" && (
                        <div style={{
                          padding: "6px 14px",
                          display: "flex",
                          alignItems: "center",
                          gap: 8,
                          fontSize: 12,
                          color: colors.text,
                          fontFamily: fonts.sans,
                        }}>
                          <span style={{ color: colors.textSecondary }}>Control:</span>
                          <select
                            value={gate.qubits[0]}
                            onChange={(e) => {
                              setControl(gate.id, Number(e.target.value));
                            }}
                            style={{
                              background: colors.card,
                              color: colors.text,
                              border: `1px solid ${colors.border}`,
                              borderRadius: 4,
                              padding: "2px 6px",
                              fontSize: 11,
                              fontFamily: fonts.mono,
                            }}
                          >
                            {Array.from({ length: circuit.numQubits }, (_, i) => i)
                              .filter((i) => i !== gate.qubits[gate.qubits.length - 1])
                              .map((i) => (
                                <option key={i} value={i}>q{i}</option>
                              ))}
                          </select>
                        </div>
                      )}

                      {/* Delete */}
                      <button
                        onClick={() => {
                          removeGate(contextMenu.gateId);
                          setContextMenu(null);
                          setSelectedGateId(null);
                        }}
                        style={{
                          width: "100%",
                          padding: "8px 14px",
                          background: "transparent",
                          border: "none",
                          color: colors.danger,
                          fontSize: 12,
                          fontFamily: fonts.sans,
                          cursor: "pointer",
                          textAlign: "left",
                          display: "flex",
                          alignItems: "center",
                          gap: 6,
                        }}
                        onMouseEnter={(e) => { (e.target as HTMLElement).style.background = `${colors.danger}15`; }}
                        onMouseLeave={(e) => { (e.target as HTMLElement).style.background = "transparent"; }}
                      >
                        Delete gate
                      </button>
                    </div>
                  </div>
                </>
              );
            })()}
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
          {circuitSnapshots.length > 1 && (
            <div
              data-onboarding="state-evolution"
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
                {circuitSnapshots.map((snap, i) => {
                  if (i === 0) return null;
                  const moment = circuit.moments[i - 1];
                  if (!moment) return null;
                  const gateDescs = moment.gates
                    .map((g) => {
                      const def = getGateDef(g.gateType);
                      const qStr = g.qubits.map((q) => `q${q}`).join(",");
                      return `${def.label}(${qStr})`;
                    })
                    .join(", ");

                  // What changed: which qubits were acted on
                  const affectedQubits = [...new Set(moment.gates.flatMap((g) => g.qubits))].sort();
                  const prevSnap = snapshots[i - 1];
                  const stateName = recognizeState(snap);

                  // Detect what changed: compare probabilities
                  let changeDesc = "";
                  if (prevSnap) {
                    const changed: string[] = [];
                    for (let b = 0; b < snap.probabilities.length; b++) {
                      const diff = snap.probabilities[b] - prevSnap.probabilities[b];
                      if (Math.abs(diff) > 0.01) {
                        changed.push(snap.labels[b]);
                      }
                    }
                    if (changed.length > 0 && changed.length <= 4) {
                      changeDesc = `Affected outcomes: ${changed.join(", ")}`;
                    } else if (changed.length > 4) {
                      changeDesc = `${changed.length} outcomes changed`;
                    }
                  }

                  return (
                    <div key={i} style={{ paddingLeft: 12, borderLeft: `2px solid ${colors.accent}40` }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
                        <span style={{ fontSize: 12, color: colors.accentLight, fontWeight: 600 }}>
                          Step {i}: {gateDescs}
                        </span>
                        <span style={{
                          fontSize: 10, color: colors.textTertiary, fontFamily: fonts.mono,
                        }}>
                          [{affectedQubits.map((q) => `q${q}`).join(",")}]
                        </span>
                        {stateName && (
                          <span style={{
                            fontSize: 10,
                            color: colors.success,
                            background: `${colors.success}15`,
                            padding: "1px 6px",
                            borderRadius: 3,
                            fontFamily: fonts.sans,
                            fontWeight: 600,
                          }}>
                            {stateName}
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: 13, color: colors.text, fontFamily: fonts.mono }}>
                        {formatDirac(snap)}
                      </div>
                      {changeDesc && (
                        <div style={{ fontSize: 10, color: colors.textTertiary, marginTop: 2, fontFamily: fonts.sans }}>
                          {changeDesc}
                        </div>
                      )}
                      {/* Dynamic narrative — contextual explanation of what this step does */}
                      {narratives[i - 1] && !displayPreset?.steps?.[i - 1] && (
                        <div style={{
                          fontSize: 11,
                          color: colors.textSecondary,
                          marginTop: 4,
                          lineHeight: 1.5,
                          fontFamily: fonts.sans,
                          paddingLeft: 4,
                          borderLeft: `2px solid ${colors.border}`,
                        }}>
                          {narratives[i - 1].explanation}
                          {narratives[i - 1].insight && (
                            <div style={{
                              marginTop: 4,
                              color: colors.accentLight,
                              fontSize: 11,
                              fontWeight: 500,
                            }}>
                              {"\u2728"} {narratives[i - 1].insight}
                            </div>
                          )}
                        </div>
                      )}
                      {/* Preset step — if available, show the hand-written explanation */}
                      {displayPreset?.steps?.[i - 1] && (
                        <div style={{
                          fontSize: 11,
                          color: colors.textSecondary,
                          marginTop: 4,
                          lineHeight: 1.5,
                          fontFamily: fonts.sans,
                          paddingLeft: 4,
                          borderLeft: `2px solid ${colors.accent}40`,
                        }}>
                          {displayPreset.steps[i - 1]}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Probability Display */}
          <ProbabilityDisplay snapshot={circuitFinalSnapshot} />

          {/* Preset Info Panel — shown for manual presets or auto-detected states */}
          {displayPreset && (
            <div
              style={{
                padding: 16,
                background: colors.surface,
                borderRadius: 8,
                border: `1px solid ${detectedPreset && !activePreset ? colors.success : colors.accent}30`,
              }}
            >
              {/* Auto-detected banner */}
              {detectedPreset && !activePreset && (
                <div style={{
                  fontSize: 10,
                  color: colors.success,
                  fontFamily: fonts.sans,
                  fontWeight: 600,
                  marginBottom: 8,
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}>
                  <span style={{
                    width: 6, height: 6, borderRadius: 3,
                    background: colors.success,
                    display: "inline-block",
                  }} />
                  State recognized — showing info for this circuit
                </div>
              )}

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
                  {displayPreset.name}
                </span>
                <span style={{
                  fontSize: 11,
                  color: colors.textTertiary,
                  fontFamily: fonts.sans,
                }}>
                  {displayPreset.learns}
                </span>
              </div>

              <p style={{
                color: colors.textSecondary,
                fontSize: 13,
                lineHeight: 1.6,
                margin: "0 0 12px",
                fontFamily: fonts.sans,
              }}>
                {displayPreset.description}
              </p>

              {/* Step-by-step explanation */}
              {displayPreset.steps && displayPreset.steps.length > 0 && (
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
                    {displayPreset.steps.map((step, i) => (
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
              {displayPreset.applications && displayPreset.applications.length > 0 && (
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
                    {displayPreset.applications.map((app, i) => (
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
            </>
          )}

          {/* ── Direct State mode ── */}
          {inputMode === "direct" && (
            <div style={{
              display: "flex",
              flexDirection: "column",
              gap: 12,
            }}>
              {/* Ideal state selector */}
              <div style={{
                padding: 14,
                background: colors.surface,
                borderRadius: 8,
                border: `1px solid ${colors.border}`,
              }}>
                <div style={{
                  fontSize: 11,
                  fontWeight: 600,
                  color: colors.textSecondary,
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                  marginBottom: 10,
                  fontFamily: fonts.sans,
                }}>
                  Load Ideal State Vector
                </div>

                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {IDEAL_STATES.map((s) => (
                    <button
                      key={s.id}
                      onClick={() => { setDirectStateId(s.id); setCustomSvText(""); setCustomSvError(null); }}
                      style={{
                        background: directStateId === s.id ? colors.accentDim : colors.card,
                        color: directStateId === s.id ? colors.accentLight : colors.text,
                        border: `1px solid ${directStateId === s.id ? colors.accent : colors.border}`,
                        borderRadius: 6,
                        padding: "5px 10px",
                        fontSize: 12,
                        fontFamily: fonts.mono,
                        fontWeight: directStateId === s.id ? 700 : 400,
                        cursor: "pointer",
                        transition: "all 0.15s",
                      }}
                    >
                      {s.name}
                      <span style={{ fontSize: 9, color: colors.textTertiary, marginLeft: 4 }}>
                        {s.numQubits}Q
                      </span>
                    </button>
                  ))}
                </div>

                {/* Selected state description */}
                {directStateId && (() => {
                  const sel = IDEAL_STATES.find((s) => s.id === directStateId);
                  return sel ? (
                    <div style={{
                      marginTop: 10,
                      padding: "8px 12px",
                      background: colors.card,
                      borderRadius: 6,
                      fontSize: 12,
                      color: colors.textSecondary,
                      lineHeight: 1.5,
                      fontFamily: fonts.sans,
                    }}>
                      {sel.description}
                    </div>
                  ) : null;
                })()}
              </div>

              {/* Custom state vector input */}
              <div style={{
                padding: 14,
                background: colors.surface,
                borderRadius: 8,
                border: `1px solid ${colors.border}`,
              }}>
                <div style={{
                  fontSize: 11,
                  fontWeight: 600,
                  color: colors.textSecondary,
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                  marginBottom: 6,
                  fontFamily: fonts.sans,
                }}>
                  Custom State Vector
                </div>
                <div style={{
                  fontSize: 10,
                  color: colors.textTertiary,
                  marginBottom: 8,
                  fontFamily: fonts.sans,
                  lineHeight: 1.4,
                }}>
                  Enter amplitudes as JSON array. Length must be 2^n.
                  Use real numbers or [real, imag] pairs. Must be normalized (sum of |a|{"\u00B2"} = 1).
                </div>
                <textarea
                  value={customSvText}
                  onChange={(e) => { setCustomSvText(e.target.value); setDirectStateId(null); }}
                  placeholder='[0.707, 0, 0, 0.707]  or  [[0.5,0], [0,0.5], [0.5,0], [0,-0.5]]'
                  style={{
                    width: "100%",
                    minHeight: 60,
                    background: colors.card,
                    color: colors.text,
                    border: `1px solid ${customSvError ? colors.danger : colors.border}`,
                    borderRadius: 6,
                    padding: 10,
                    fontSize: 12,
                    fontFamily: fonts.mono,
                    resize: "vertical",
                    outline: "none",
                  }}
                />
                {customSvError && (
                  <div style={{
                    fontSize: 11,
                    color: colors.danger,
                    marginTop: 4,
                    fontFamily: fonts.sans,
                  }}>
                    {customSvError}
                  </div>
                )}
              </div>

              {/* Show state info if we have a snapshot */}
              {directSnapshot && (
                <div style={{
                  padding: 14,
                  background: colors.surface,
                  borderRadius: 8,
                  border: `1px solid ${colors.border}`,
                }}>
                  <div style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: colors.textSecondary,
                    textTransform: "uppercase",
                    letterSpacing: "0.5px",
                    marginBottom: 8,
                    fontFamily: fonts.sans,
                  }}>
                    State Analysis
                  </div>

                  {/* Recognized state */}
                  {(() => {
                    const name = recognizeState(directSnapshot);
                    return name ? (
                      <div style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 6,
                        marginBottom: 8,
                      }}>
                        <span style={{
                          fontSize: 10,
                          color: colors.success,
                          background: `${colors.success}15`,
                          padding: "2px 8px",
                          borderRadius: 3,
                          fontFamily: fonts.sans,
                          fontWeight: 600,
                        }}>
                          {name}
                        </span>
                      </div>
                    ) : null;
                  })()}

                  {/* Dirac notation */}
                  <div style={{
                    fontSize: 13,
                    color: colors.text,
                    fontFamily: fonts.mono,
                    marginBottom: 8,
                  }}>
                    {formatDirac(directSnapshot)}
                  </div>

                  {/* Probabilities */}
                  <ProbabilityDisplay snapshot={directSnapshot} />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: Bloch sphere playback panel with resize handle */}
        <div data-onboarding="bloch-sphere" style={{ width: blochPanelWidth, flexShrink: 0, position: "relative" }}>
          {/* Drag handle on left edge */}
          <div
            onPointerDown={(e) => {
              e.preventDefault();
              resizingRef.current = true;
              resizeStartRef.current = { x: e.clientX, width: blochPanelWidth };
              (e.target as HTMLElement).setPointerCapture(e.pointerId);
            }}
            onPointerMove={(e) => {
              if (!resizingRef.current) return;
              const dx = resizeStartRef.current.x - e.clientX;
              const newWidth = Math.max(280, Math.min(700, resizeStartRef.current.width + dx));
              setBlochPanelWidth(newWidth);
            }}
            onPointerUp={() => { resizingRef.current = false; }}
            onPointerCancel={() => { resizingRef.current = false; }}
            style={{
              position: "absolute",
              left: -3,
              top: 0,
              bottom: 0,
              width: 6,
              cursor: "col-resize",
              zIndex: 2,
              background: "transparent",
            }}
            title="Drag to resize"
          >
            {/* Visual indicator */}
            <div style={{
              position: "absolute",
              left: 2,
              top: "50%",
              transform: "translateY(-50%)",
              width: 3,
              height: 40,
              borderRadius: 2,
              background: colors.border,
              opacity: 0.5,
              transition: "opacity 0.15s",
            }} />
          </div>
          <BlochPlaybackPanel
            playback={playback}
            numQubits={activeNumQubits}
            fullscreenOpen={blochFullscreen}
            onFullscreenChange={setBlochFullscreen}
            previewCaption={gatePreview?.caption ?? null}
            activeQubits={(() => {
              const { snapshotIndex, t, status } = playback.state;
              // Only highlight during active playback or mid-step scrubbing
              if (status === "idle") return undefined;
              if (t === 0 && snapshotIndex === 0) return undefined;
              // At the final step with no interpolation — playback finished
              const totalSnaps = playback.totalSnapshots;
              if (snapshotIndex >= totalSnaps - 1 && t === 0) return undefined;
              // The moment being animated
              const momentIdx = t > 0 ? snapshotIndex : Math.max(0, snapshotIndex - 1);
              const moments = isPreviewActive && activeGateType
                ? GATE_PREVIEW_CIRCUITS[activeGateType]?.circuit?.moments
                : circuit.moments;
              const moment = moments?.[momentIdx];
              if (!moment) return undefined;
              return [...new Set(moment.gates.flatMap((g: { qubits: number[] }) => g.qubits))] as number[];
            })()}
            activeGateLabel={(() => {
              const { snapshotIndex, t, status } = playback.state;
              if (status === "idle") return null;
              if (t === 0 && snapshotIndex === 0) return null;
              const totalSnaps = playback.totalSnapshots;
              if (snapshotIndex >= totalSnaps - 1 && t === 0) return null;
              const momentIdx = t > 0 ? snapshotIndex : Math.max(0, snapshotIndex - 1);
              const moments = isPreviewActive && activeGateType
                ? GATE_PREVIEW_CIRCUITS[activeGateType]?.circuit?.moments
                : circuit.moments;
              const moment = moments?.[momentIdx];
              if (!moment) return null;
              return moment.gates.map((g: { gateType: string; qubits: number[] }) => {
                const def = getGateDef(g.gateType as any);
                return `${def.label}(${g.qubits.map((q: number) => `q${q}`).join(",")})`;
              }).join(", ");
            })()}
            activeGateColor={(() => {
              const { snapshotIndex, t, status } = playback.state;
              if (status === "idle") return null;
              if (t === 0 && snapshotIndex === 0) return null;
              const totalSnaps = playback.totalSnapshots;
              if (snapshotIndex >= totalSnaps - 1 && t === 0) return null;
              const momentIdx = t > 0 ? snapshotIndex : Math.max(0, snapshotIndex - 1);
              const moments = isPreviewActive && activeGateType
                ? GATE_PREVIEW_CIRCUITS[activeGateType]?.circuit?.moments
                : circuit.moments;
              const moment = moments?.[momentIdx];
              if (!moment || !moment.gates[0]) return null;
              return getGateDef(moment.gates[0].gateType as any).color;
            })()}
          />
        </div>
      </div>
    </div>
  );
}
