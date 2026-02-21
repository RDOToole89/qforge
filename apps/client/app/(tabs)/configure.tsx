import React, { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  View,
} from "react-native";

import ConfigSlider from "@/src/components/ConfigSlider";
import MetricCard from "@/src/components/MetricCard";
import ResultChart from "@/src/components/ResultChart";
import { runExperiment } from "@/src/lib/api";
import type {
  ExperimentConfig,
  ExperimentResult,
  NoiseType,
  StateType,
} from "@/src/lib/types";

const STATE_TYPES: StateType[] = [
  "GHZ",
  "W",
  "CLUSTER",
  "BELL",
  "SUPERPOSITION",
];
const NOISE_TYPES: NoiseType[] = [
  "depolarizing",
  "amplitude_damping",
  "phase_damping",
  "bit_flip",
  "phase_flip",
];
const SHOT_OPTIONS = [1024, 4096, 8192, 16384];

export default function ConfigureScreen() {
  // ── Config state ──────────────────────────────────────────────────
  const [numQubits, setNumQubits] = useState(3);
  const [stateType, setStateType] = useState<StateType>("GHZ");
  const [shots, setShots] = useState(1024);
  const [noiseEnabled, setNoiseEnabled] = useState(true);
  const [noiseType, setNoiseType] = useState<NoiseType>("depolarizing");
  const [errorRate, setErrorRate] = useState(0.05);
  const [researchMetrics, setResearchMetrics] = useState(true);

  // ── Execution state ───────────────────────────────────────────────
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<ExperimentResult | null>(null);

  const handleRun = async () => {
    setRunning(true);
    setResult(null);
    try {
      const config: ExperimentConfig = {
        num_qubits: numQubits,
        state_type: stateType,
        shots,
        noise_enabled: noiseEnabled,
        ...(noiseEnabled && { noise_type: noiseType, error_rate: errorRate }),
        metrics: researchMetrics ? "structured_decoherence" : undefined,
        visualization_type: "none",
      };
      const res = await runExperiment(config);
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

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      {/* ── State Type ──────────────────────────────────────────── */}
      <Text style={styles.section}>State Type</Text>
      <View style={styles.segmented}>
        {STATE_TYPES.map((st) => (
          <Pressable
            key={st}
            onPress={() => setStateType(st)}
            style={[styles.seg, stateType === st && styles.segActive]}
          >
            <Text
              style={[styles.segText, stateType === st && styles.segTextActive]}
            >
              {st}
            </Text>
          </Pressable>
        ))}
      </View>

      {/* ── Qubits ─────────────────────────────────────────────── */}
      <ConfigSlider
        label="Qubits"
        value={numQubits}
        min={1}
        max={12}
        step={1}
        onValueChange={(v) => setNumQubits(Math.round(v))}
      />

      {/* ── Shots ──────────────────────────────────────────────── */}
      <Text style={styles.section}>Shots</Text>
      <View style={styles.segmented}>
        {SHOT_OPTIONS.map((s) => (
          <Pressable
            key={s}
            onPress={() => setShots(s)}
            style={[styles.seg, shots === s && styles.segActive]}
          >
            <Text style={[styles.segText, shots === s && styles.segTextActive]}>
              {s >= 1000 ? `${s / 1000}k` : s}
            </Text>
          </Pressable>
        ))}
      </View>

      {/* ── Noise ──────────────────────────────────────────────── */}
      <View style={styles.toggleRow}>
        <Text style={styles.section}>Noise</Text>
        <Switch
          value={noiseEnabled}
          onValueChange={setNoiseEnabled}
          trackColor={{ false: "#334155", true: "#6366f1" }}
          thumbColor="#e2e8f0"
        />
      </View>

      {noiseEnabled && (
        <>
          <Text style={styles.subsection}>Noise Type</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.chipScroll}
          >
            {NOISE_TYPES.map((nt) => (
              <Pressable
                key={nt}
                onPress={() => setNoiseType(nt)}
                style={[styles.chip, noiseType === nt && styles.chipActive]}
              >
                <Text
                  style={[
                    styles.chipText,
                    noiseType === nt && styles.chipTextActive,
                  ]}
                >
                  {nt.replace(/_/g, " ")}
                </Text>
              </Pressable>
            ))}
          </ScrollView>

          <ConfigSlider
            label="Error Rate"
            value={errorRate}
            min={0}
            max={0.5}
            step={0.01}
            onValueChange={setErrorRate}
            formatValue={(v) => v.toFixed(2)}
          />
        </>
      )}

      {/* ── Research Metrics ───────────────────────────────────── */}
      <View style={styles.toggleRow}>
        <Text style={styles.section}>Research Metrics</Text>
        <Switch
          value={researchMetrics}
          onValueChange={setResearchMetrics}
          trackColor={{ false: "#334155", true: "#6366f1" }}
          thumbColor="#e2e8f0"
        />
      </View>

      {/* ── Run Button ─────────────────────────────────────────── */}
      <Pressable
        style={({ pressed }) => [
          styles.runBtn,
          running && styles.runBtnDisabled,
          pressed && !running && styles.pressed,
        ]}
        onPress={handleRun}
        disabled={running}
      >
        {running ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.runBtnText}>Run Experiment</Text>
        )}
      </Pressable>

      {/* ── Results ────────────────────────────────────────────── */}
      {result && (
        <View style={styles.results}>
          <Text style={styles.resultHeader}>Results</Text>

          {/* Circuit stats */}
          <View style={styles.statsRow}>
            <Stat
              label="Depth"
              value={result.analysis.circuit_statistics.depth}
            />
            <Stat
              label="Gates"
              value={result.analysis.circuit_statistics.num_gates}
            />
            <Stat
              label="Outcomes"
              value={result.analysis.measurement_results.unique_outcomes}
            />
          </View>

          {/* Counts chart */}
          <ResultChart
            counts={result.analysis.measurement_results.raw_counts}
          />

          {/* Research metrics */}
          {metrics && (
            <View style={{ marginTop: 16 }}>
              <Text style={styles.resultHeader}>
                {metrics.profile ? `Metrics (${metrics.profile})` : "Metrics"}
              </Text>
              {Object.entries(metrics.metrics).map(([name, entry]) => (
                <MetricCard
                  key={name}
                  name={name}
                  value={entry.value}
                  subtitle={entry.status}
                />
              ))}
            </View>
          )}
        </View>
      )}
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
  screen: { flex: 1, backgroundColor: "#0f172a" },
  content: { padding: 16, paddingBottom: 80 },
  section: { color: "#e2e8f0", fontSize: 16, fontWeight: "700", marginTop: 16, marginBottom: 8 },
  subsection: { color: "#94a3b8", fontSize: 13, fontWeight: "600", marginBottom: 6 },

  segmented: { flexDirection: "row", gap: 6, flexWrap: "wrap", marginBottom: 16 },
  seg: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 8,
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
  },
  segActive: { backgroundColor: "#6366f1", borderColor: "#6366f1" },
  segText: { color: "#94a3b8", fontSize: 13, fontWeight: "600" },
  segTextActive: { color: "#fff" },

  chipScroll: { marginBottom: 12 },
  chip: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 16,
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
    marginRight: 8,
  },
  chipActive: { backgroundColor: "#4f46e5", borderColor: "#6366f1" },
  chipText: { color: "#94a3b8", fontSize: 12 },
  chipTextActive: { color: "#fff" },

  toggleRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 8,
  },

  runBtn: {
    backgroundColor: "#6366f1",
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 24,
  },
  runBtnDisabled: { opacity: 0.5 },
  runBtnText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  pressed: { opacity: 0.8 },

  results: { marginTop: 24 },
  resultHeader: { color: "#e2e8f0", fontSize: 18, fontWeight: "700", marginBottom: 12 },

  statsRow: { flexDirection: "row", gap: 12, marginBottom: 16 },
  stat: {
    flex: 1,
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#334155",
  },
  statValue: { color: "#e2e8f0", fontSize: 22, fontWeight: "700", fontFamily: "SpaceMono" },
  statLabel: { color: "#64748b", fontSize: 11, marginTop: 4 },
});
