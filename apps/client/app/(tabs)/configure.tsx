import React, { useState, useMemo } from "react";
import { Alert, ScrollView, View } from "react-native";

import { Button, Card, Row, Text } from "@/src/design";
import MetricCard from "@/src/components/MetricCard";
import ResultChart from "@/src/components/ResultChart";
import { useExperimentConfig, type ConfigWarning } from "@/src/features/configure/useExperimentConfig";
import { useHardwareValidation } from "@/src/features/configure/useHardwareValidation";
import { INFO_TEXT } from "@/src/features/configure/constants";
import { StateSection } from "@/src/features/configure/components/StateSection";
import { SimulationSection } from "@/src/features/configure/components/SimulationSection";
import { NoiseSection } from "@/src/features/configure/components/NoiseSection";
import { MetricsSection } from "@/src/features/configure/components/MetricsSection";
import { HardwareSection } from "@/src/features/configure/components/HardwareSection";
import { ValidationBanner } from "@/src/features/configure/components/ValidationBanner";
import { CircuitPreview } from "@/src/features/configure/components/CircuitPreview";
import { InfoModal } from "@/src/features/configure/components/InfoModal";
import { runExperiment } from "@/src/lib/api";
import type { ExperimentResult } from "@/src/lib/types";

export default function ConfigureScreen() {
  const config = useExperimentConfig();

  // Memoize config JSON to avoid redundant circuit preview fetches
  const configJson = useMemo(
    () => JSON.stringify(config.buildConfig()),
    [config.stateType, config.numQubits, config.simMode, config.noiseEnabled, config.noiseType, config.errorRate],
  );

  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<ExperimentResult | null>(null);
  const [infoKey, setInfoKey] = useState<string | null>(null);
  const [metricsOpen, setMetricsOpen] = useState(false);

  // Real hardware backend list + pre-submission feasibility check.
  const hw = useHardwareValidation(
    config.simMode === "hardware",
    config.buildConfig,
  );

  // Hardware feasibility violations/warnings, surfaced in the validation banner.
  const hardwareWarnings = useMemo<ConfigWarning[]>(() => {
    if (config.simMode !== "hardware") return [];
    const w: ConfigWarning[] = [];
    const v = hw.validation;
    if (v) {
      if (!v.available && v.reason) {
        w.push({
          level: "info",
          message: `Hardware feasibility not verified: ${v.reason}`,
        });
      }
      if (v.available) {
        for (const msg of v.violations ?? []) {
          w.push({ level: "error", message: msg });
        }
        for (const msg of v.warnings ?? []) {
          w.push({ level: "warning", message: msg });
        }
      }
    }
    return w;
  }, [config.simMode, hw.validation]);

  const allWarnings = useMemo(
    () => [...config.warnings, ...hardwareWarnings],
    [config.warnings, hardwareWarnings],
  );

  // Block hardware runs only when the backend explicitly reports infeasibility.
  const hardwareBlocked =
    config.simMode === "hardware" &&
    hw.validation?.available === true &&
    hw.validation?.feasible === false;

  const canRun = config.isValid && !hardwareBlocked && !running;

  const handleRun = async () => {
    if (!config.isValid || hardwareBlocked) return;
    setRunning(true);
    setResult(null);
    try {
      const res = await runExperiment(config.buildConfig());
      setResult(res);
    } catch (err) {
      Alert.alert(
        "Experiment Failed",
        err instanceof Error ? err.message : String(err),
      );
    } finally {
      setRunning(false);
    }
  };

  const metrics = result?.metrics_bundle;
  const infoEntry = infoKey ? INFO_TEXT[infoKey] : null;

  return (
    <ScrollView
      className="flex-1 bg-base"
      contentContainerStyle={{ padding: 16, paddingBottom: 80 }}
    >
      <Text weight="bold" tone="primary" className="mb-sm text-headingLg">
        Configure
      </Text>

      <StateSection
        stateType={config.stateType}
        setStateType={config.setStateType}
        numQubits={config.numQubits}
        setNumQubits={config.setNumQubits}
        onInfo={() => setInfoKey("state")}
      />

      <SimulationSection
        simMode={config.simMode}
        setSimMode={config.setSimMode}
        shots={config.shots}
        setShots={config.setShots}
        rngSeed={config.rngSeed}
        setRngSeed={config.setRngSeed}
        showHardwareSection={config.showHardwareSection}
        onInfo={() => setInfoKey("simulation")}
      />

      <NoiseSection
        noiseEnabled={config.noiseEnabled}
        setNoiseEnabled={config.setNoiseEnabled}
        noiseType={config.noiseType}
        setNoiseType={config.setNoiseType}
        errorRate={config.errorRate}
        setErrorRate={config.setErrorRate}
        t1={config.t1}
        setT1={config.setT1}
        t2={config.t2}
        setT2={config.setT2}
        readoutErrorRate={config.readoutErrorRate}
        setReadoutErrorRate={config.setReadoutErrorRate}
        balanceCircuit={config.balanceCircuit}
        setBalanceCircuit={config.setBalanceCircuit}
        noiseDisabledReason={config.noiseDisabledReason}
        showThermalParams={config.showThermalParams}
        onInfo={() => setInfoKey("noise")}
      />

      <MetricsSection
        metricsEnabled={config.metricsEnabled}
        setMetricsEnabled={config.setMetricsEnabled}
        metricsMode={config.metricsMode}
        setMetricsMode={config.setMetricsMode}
        selectedProfile={config.selectedProfile}
        setSelectedProfile={config.setSelectedProfile}
        selectedMetrics={config.selectedMetrics}
        setSelectedMetrics={config.setSelectedMetrics}
        experimentType={config.experimentType}
        setExperimentType={config.setExperimentType}
        multipleRuns={config.multipleRuns}
        setMultipleRuns={config.setMultipleRuns}
        trackConvergence={config.trackConvergence}
        setTrackConvergence={config.setTrackConvergence}
        collapsed={!metricsOpen}
        onToggleCollapse={() => setMetricsOpen((v) => !v)}
        onInfo={() => setInfoKey("metrics")}
      />

      {config.showHardwareSection && (
        <HardwareSection
          backendName={config.backendName}
          setBackendName={config.setBackendName}
          optimizationLevel={config.optimizationLevel}
          setOptimizationLevel={config.setOptimizationLevel}
          hardwareSession={config.hardwareSession}
          setHardwareSession={config.setHardwareSession}
          onInfo={() => setInfoKey("hardware")}
          backends={hw.backends}
          backendsAvailable={hw.backendsAvailable}
          backendsReason={hw.backendsReason}
          backendsLoading={hw.backendsLoading}
        />
      )}

      <ValidationBanner warnings={allWarnings} />

      {/* Circuit Preview -- auto-updates when config changes */}
      <CircuitPreview configJson={configJson} />

      {/* Run Button */}
      <Button
        variant="primary"
        size="lg"
        fullWidth
        loading={running}
        disabled={!canRun}
        onPress={handleRun}
        className="mt-2xl"
      >
        Run Experiment
      </Button>

      {/* Results */}
      {result && (
        <View className="mt-2xl">
          <Text variant="heading" weight="bold" className="mb-md">
            Results
          </Text>

          <Row gap="md" className="mb-lg">
            <Stat label="Depth" value={result.analysis.circuit_statistics.depth} />
            <Stat label="Gates" value={result.analysis.circuit_statistics.num_gates} />
            <Stat label="Outcomes" value={result.analysis.measurement_results.unique_outcomes} />
          </Row>

          <ResultChart counts={result.analysis.measurement_results.raw_counts} />

          {metrics && (
            <View className="mt-lg">
              <Text variant="heading" weight="bold" className="mb-md">
                {metrics.profile ? `Metrics (${metrics.profile})` : "Metrics"}
              </Text>
              {Object.entries(metrics.metrics).map(([name, entry]) => (
                <MetricCard key={name} name={name} value={entry.value} subtitle={entry.status} />
              ))}
            </View>
          )}
        </View>
      )}

      {/* Info Modal */}
      <InfoModal
        visible={!!infoKey}
        infoKey={infoKey}
        onClose={() => setInfoKey(null)}
      />

      {/* (Bloch expand handled natively by MiniBlochSphere's click-to-expand) */}
    </ScrollView>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <Card variant="outlined" padding="md" className="flex-1 items-center">
      <Text weight="bold" mono tone="primary" style={{ fontSize: 22 }}>
        {value}
      </Text>
      <Text variant="bodySm" tone="tertiary" className="mt-xs">
        {label}
      </Text>
    </Card>
  );
}
