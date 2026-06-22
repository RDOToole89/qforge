import React, { useState, useMemo } from "react";
import {
  ActivityIndicator,
  Alert,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

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
import { colors } from "@/src/theme";

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
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Configure</Text>

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
        researchType={config.researchType}
        setResearchType={config.setResearchType}
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
      <Pressable
        style={({ pressed }) => [
          styles.runBtn,
          !canRun && styles.runBtnDisabled,
          pressed && canRun && styles.pressed,
        ]}
        onPress={handleRun}
        disabled={!canRun}
      >
        {running ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.runBtnText}>Run Experiment</Text>
        )}
      </Pressable>

      {/* Results */}
      {result && (
        <View style={styles.results}>
          <Text style={styles.resultHeader}>Results</Text>

          <View style={styles.statsRow}>
            <Stat label="Depth" value={result.analysis.circuit_statistics.depth} />
            <Stat label="Gates" value={result.analysis.circuit_statistics.num_gates} />
            <Stat label="Outcomes" value={result.analysis.measurement_results.unique_outcomes} />
          </View>

          <ResultChart counts={result.analysis.measurement_results.raw_counts} />

          {metrics && (
            <View style={{ marginTop: 16 }}>
              <Text style={styles.resultHeader}>
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
    <View style={styles.stat}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg.primary },
  content: { padding: 16, paddingBottom: 80 },
  title: {
    color: colors.text.primary,
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 8,
  },

  runBtn: {
    backgroundColor: colors.accent.base,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 24,
  },
  runBtnDisabled: { opacity: 0.5 },
  runBtnText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  pressed: { opacity: 0.8 },

  results: { marginTop: 24 },
  resultHeader: {
    color: colors.text.primary,
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 12,
  },

  statsRow: { flexDirection: "row", gap: 12, marginBottom: 16 },
  stat: {
    flex: 1,
    backgroundColor: colors.bg.surface,
    borderRadius: 12,
    padding: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.border,
  },
  statValue: {
    color: colors.text.primary,
    fontSize: 22,
    fontWeight: "700",
    fontFamily: "SpaceMono",
  },
  statLabel: { color: colors.text.tertiary, fontSize: 11, marginTop: 4 },
});
