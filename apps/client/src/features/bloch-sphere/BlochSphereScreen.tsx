'use dom';

import { useCallback } from "react";
import { useBuiltInMode } from "./hooks/useBuiltInMode";
import { useExperimentMode } from "./hooks/useExperimentMode";
import { useSweepMode } from "./hooks/useSweepMode";
import { useDragRotation } from "./hooks/useDragRotation";
import { bdr } from "./styles";
import Header from "./components/Header";
import BuiltinSidebar from "./components/BuiltinSidebar";
import ExperimentSidebar from "./components/ExperimentSidebar";
import DataPanel from "./components/DataPanel";
import UnifiedBlochSphere from "./components/UnifiedBlochSphere";
import TwoQubitScene from "./components/TwoQubitScene";
import ConfigEditor from "./components/ConfigEditor";

export default function BlochSphereScreen() {
  const builtin = useBuiltInMode();
  const sweep = useSweepMode();
  const drag = useDragRotation();

  const hasSweep = sweep.sweepData !== null && sweep.sweepData.snapshots.length > 1;

  const experiment = useExperimentMode(sweep.sweepSnapshot, hasSweep);

  const isExpMode = experiment.mode === "experiment";
  const _activeBloch = experiment.activeBloch;
  const activeStateCfg = isExpMode && experiment.expStateCfg ? experiment.expStateCfg : builtin.stateCfg;

  // Wrap launchSweep to pass experiment state callbacks
  const handleLaunchSweep = useCallback(() => {
    sweep.launchSweep({
      setSelectedResult: experiment.setSelectedResult,
      setBlochData: experiment.setBlochData,
      setSelectedQubit: experiment.setSelectedQubit,
      setExpError: experiment.setExpError,
    });
  }, [sweep, experiment.setSelectedResult, experiment.setBlochData, experiment.setSelectedQubit, experiment.setExpError]);

  // When selecting a result, also clear sweep data
  const handleSelectResult = useCallback((v: string | null) => {
    experiment.setSelectedResult(v);
    sweep.setSweepData(null);
    sweep.setSweepAnimating(false);
  }, [experiment.setSelectedResult, sweep.setSweepData, sweep.setSweepAnimating]);

  return (
    <div style={{
      width: "100vw", height: "100vh", background: "#08090e", color: "#c8d4e4",
      fontFamily: "'IBM Plex Sans', system-ui, sans-serif",
      display: "flex", flexDirection: "column", overflow: "hidden", userSelect: "none",
    }}>

      <Header
        mode={experiment.mode}
        setMode={experiment.setMode}
        tab={builtin.tab}
        setTab={builtin.setTab}
        storedResultsCount={experiment.storedResults.length}
        isExp={isExpMode}
        onConfigOpen={() => builtin.setShowConfig(true)}
      />

      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        {/* Left sidebar */}
        <div style={{
          width: "250px", flexShrink: 0, padding: "12px 14px", borderRight: bdr,
          display: "flex", flexDirection: "column", gap: "10px", overflowY: "auto",
        }}>
          {isExpMode ? (
            <ExperimentSidebar
              storedResults={experiment.storedResults}
              selectedResult={experiment.selectedResult}
              setSelectedResult={handleSelectResult}
              sweepStateType={sweep.sweepStateType}
              setSweepStateType={sweep.setSweepStateType}
              sweepQubits={sweep.sweepQubits}
              setSweepQubits={sweep.setSweepQubits}
              sweepNoiseType={sweep.sweepNoiseType}
              setSweepNoiseType={sweep.setSweepNoiseType}
              sweepLoading={sweep.sweepLoading}
              launchSweep={handleLaunchSweep}
              hasSweep={isExpMode && hasSweep}
              activeBloch={_activeBloch}
              sweepProgress={sweep.sweepProgress}
              setSweepProgress={sweep.setSweepProgress}
              sweepAnimating={sweep.sweepAnimating}
              setSweepAnimating={sweep.setSweepAnimating}
              sweepAnimRef={sweep.sweepAnimRef}
              toggleSweepAnim={sweep.toggleSweepAnim}
              expLoading={experiment.expLoading}
              expError={experiment.expError}
              tab={builtin.tab}
              selectedQubit={experiment.selectedQubit}
              setSelectedQubit={experiment.setSelectedQubit}
              selectedPair={experiment.selectedPair}
              setSelectedPair={experiment.setSelectedPair}
              expQubitPairs={experiment.expQubitPairs}
            />
          ) : (
            <BuiltinSidebar
              config={builtin.config}
              stateKey={builtin.stateKey}
              setStateKey={builtin.setStateKey}
              channel={builtin.channel}
              setChannel={builtin.setChannel}
              runtimeCh={builtin.runtimeCh}
              tab={builtin.tab}
              activeTopo={builtin.activeTopo}
              setActiveTopo={builtin.setActiveTopo}
              viewMode={builtin.viewMode}
              setViewMode={builtin.setViewMode}
              showOrig={builtin.showOrig}
              setShowOrig={builtin.setShowOrig}
              showTrans={builtin.showTrans}
              setShowTrans={builtin.setShowTrans}
              strength={builtin.strength}
              setStrength={builtin.setStrength}
              animating={builtin.animating}
              setAnimating={builtin.setAnimating}
              animRef={builtin.animRef}
              toggleAnim={builtin.toggleAnim}
            />
          )}
        </div>

        {/* Center 3D */}
        <div
          style={{
            flex: 1, position: "relative",
            cursor: drag.isDragging ? "grabbing" : "grab",
          }}
          onPointerDown={drag.onPD}
          onPointerMove={drag.onPM}
          onPointerUp={drag.onPU}
          onPointerLeave={drag.onPU}
        >
          {(builtin.tab === "single" || builtin.tab === "ptm" || builtin.tab === "data") && (
            <UnifiedBlochSphere
              mode="visualizer"
              runtimeCh={builtin.runtimeCh}
              channel={builtin.channel}
              strength={builtin.strength}
              showOrig={builtin.showOrig}
              showTrans={builtin.showTrans}
              rotation={drag.rotation}
              stateCfg={activeStateCfg}
              viewMode={isExpMode ? "state" : builtin.viewMode}
              experimentMode={isExpMode}
              additionalStates={isExpMode ? experiment.expAllQubits : undefined}
            />
          )}
          {builtin.tab === "multi" && !isExpMode && (
            <TwoQubitScene
              topoConfigs={builtin.config.topologies}
              activeTopo={builtin.activeTopo}
              strength={builtin.strength}
              rotation={drag.rotation}
              stateCfg={builtin.stateCfg}
            />
          )}
          {builtin.tab === "multi" && isExpMode && experiment.expPairData && (
            <TwoQubitScene
              topoConfigs={builtin.config.topologies}
              activeTopo="all"
              strength={0}
              rotation={drag.rotation}
              stateCfg={experiment.expPairData.stateCfg}
            />
          )}

          {/* Axis legend overlay */}
          <div style={{ position: "absolute", top: "10px", right: "14px", fontSize: "10px", color: "#3a4a5a" }}>
            {builtin.tab === "multi"
              ? <><span style={{ color: "#ff4466" }}>{"\u2501"}</span> {"\u27E8"}ZI{"\u27E9"} <span style={{ color: "#44ff88" }}>{"\u2501"}</span> {"\u27E8"}IZ{"\u27E9"} <span style={{ color: "#4488ff" }}>{"\u2501"}</span> {"\u27E8"}ZZ{"\u27E9"}</>
              : <><span style={{ color: "#ff4466" }}>{"\u2501"}</span> X <span style={{ color: "#44ff88" }}>{"\u2501"}</span> Y <span style={{ color: "#4488ff" }}>{"\u2501"}</span> Z</>
            }
          </div>

          {/* State name overlay */}
          <div style={{
            position: "absolute", top: "10px", left: "14px",
            fontSize: "11px", color: activeStateCfg.color ?? "#fff", fontWeight: 600,
          }}>
            {activeStateCfg.name}
            {activeStateCfg.uniform && !isExpMode && (
              <span style={{ fontSize: "9px", opacity: 0.5, fontWeight: 400, marginLeft: "6px" }}>
                uniform Z-dist
              </span>
            )}
            {isExpMode && _activeBloch?.source_mode === "diagonal_estimate" && (
              <span style={{ fontSize: "9px", color: "#dda030", fontWeight: 400, marginLeft: "6px" }}>
                Z-basis only
              </span>
            )}
          </div>

          <div style={{ position: "absolute", bottom: "10px", left: "14px", fontSize: "9px", color: "#2a3a4a" }}>
            Drag to rotate
          </div>
        </div>

        {/* Right sidebar */}
        <DataPanel
          isExp={isExpMode}
          tab={builtin.tab}
          activeStateCfg={activeStateCfg}
          config={builtin.config}
          ch={builtin.ch}
          runtimeCh={builtin.runtimeCh}
          channel={builtin.channel}
          strength={builtin.strength}
          stateCfg={builtin.stateCfg}
          activeTopo={builtin.activeTopo}
          activeBloch={_activeBloch}
          selectedQubit={experiment.selectedQubit}
          selectedPair={experiment.selectedPair}
          expPairData={experiment.expPairData}
          expFingerprints={experiment.expFingerprints}
        />
      </div>

      {/* CONFIG MODAL */}
      {builtin.showConfig && (
        <ConfigEditor
          config={builtin.config}
          onUpdate={(c) => { builtin.setConfig(c); builtin.setShowConfig(false); }}
          onClose={() => builtin.setShowConfig(false)}
        />
      )}
    </div>
  );
}
