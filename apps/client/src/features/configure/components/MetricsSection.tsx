import React from "react";
import { View, Text, Pressable, Switch, StyleSheet } from "react-native";
import { colors, spacing } from "@/src/theme";
import type { ResearchType } from "@/src/lib/types";
import {
  RESEARCH_TYPES,
  METRIC_PROFILES,
  INDIVIDUAL_METRICS,
} from "../constants";
import { SectionHeader } from "./SectionHeader";

interface MetricsSectionProps {
  metricsEnabled: boolean;
  setMetricsEnabled: (v: boolean) => void;
  metricsMode: "profile" | "individual";
  setMetricsMode: (v: "profile" | "individual") => void;
  selectedProfile: string;
  setSelectedProfile: (v: string) => void;
  selectedMetrics: string[];
  setSelectedMetrics: (v: string[]) => void;
  researchType: ResearchType | null;
  setResearchType: (v: ResearchType | null) => void;
  multipleRuns: number;
  setMultipleRuns: (v: number) => void;
  trackConvergence: boolean;
  setTrackConvergence: (v: boolean) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  onInfo: () => void;
}

export function MetricsSection({
  metricsEnabled,
  setMetricsEnabled,
  metricsMode,
  setMetricsMode,
  selectedProfile,
  setSelectedProfile,
  selectedMetrics,
  setSelectedMetrics,
  researchType,
  setResearchType,
  multipleRuns,
  setMultipleRuns,
  trackConvergence,
  setTrackConvergence,
  collapsed,
  onToggleCollapse,
  onInfo,
}: MetricsSectionProps) {
  const toggleMetric = (id: string) => {
    if (selectedMetrics.includes(id)) {
      setSelectedMetrics(selectedMetrics.filter((m) => m !== id));
    } else {
      setSelectedMetrics([...selectedMetrics, id]);
    }
  };

  const decRuns = () => setMultipleRuns(Math.max(1, multipleRuns - 1));
  const incRuns = () => setMultipleRuns(Math.min(100, multipleRuns + 1));

  return (
    <View style={styles.section}>
      <SectionHeader
        title="Research Metrics"
        switchValue={metricsEnabled}
        onSwitchChange={setMetricsEnabled}
        collapsed={collapsed}
        onToggleCollapse={onToggleCollapse}
        onInfo={onInfo}
      />

      {metricsEnabled && !collapsed && (
        <>
          {/* Research type */}
          <Text style={styles.label}>Research Type</Text>
          <View style={styles.chipRow}>
            {RESEARCH_TYPES.map((rt) => {
              const active = researchType === rt.id;
              return (
                <Pressable
                  key={rt.id}
                  onPress={() => setResearchType(active ? null : rt.id)}
                  style={[styles.chip, active && styles.chipActive]}
                >
                  <Text
                    style={[styles.chipText, active && styles.chipTextActive]}
                  >
                    {rt.label}
                  </Text>
                </Pressable>
              );
            })}
          </View>

          {/* Metrics mode segmented control */}
          <Text style={styles.label}>Metrics Selection</Text>
          <View style={styles.modeRow}>
            <Pressable
              onPress={() => setMetricsMode("profile")}
              style={[
                styles.modeChip,
                metricsMode === "profile" && styles.chipActive,
              ]}
            >
              <Text
                style={[
                  styles.chipText,
                  metricsMode === "profile" && styles.chipTextActive,
                ]}
              >
                Profile
              </Text>
            </Pressable>
            <Pressable
              onPress={() => setMetricsMode("individual")}
              style={[
                styles.modeChip,
                metricsMode === "individual" && styles.chipActive,
              ]}
            >
              <Text
                style={[
                  styles.chipText,
                  metricsMode === "individual" && styles.chipTextActive,
                ]}
              >
                Individual
              </Text>
            </Pressable>
          </View>

          {/* Profile mode */}
          {metricsMode === "profile" && (
            <View style={styles.chipRow}>
              {METRIC_PROFILES.map((profile) => {
                const active = selectedProfile === profile.id;
                return (
                  <Pressable
                    key={profile.id}
                    onPress={() => setSelectedProfile(profile.id)}
                    style={[styles.chip, active && styles.chipActive]}
                  >
                    <Text
                      style={[
                        styles.chipText,
                        active && styles.chipTextActive,
                      ]}
                    >
                      {profile.label} ({profile.metrics.length} metrics)
                    </Text>
                  </Pressable>
                );
              })}
            </View>
          )}

          {/* Individual mode */}
          {metricsMode === "individual" && (
            <View style={styles.metricsList}>
              {INDIVIDUAL_METRICS.map((metric) => {
                const checked = selectedMetrics.includes(metric.id);
                return (
                  <Pressable
                    key={metric.id}
                    onPress={() => toggleMetric(metric.id)}
                    style={styles.metricRow}
                  >
                    <Text
                      style={[
                        styles.checkbox,
                        checked && styles.checkboxActive,
                      ]}
                    >
                      {checked ? "\u25A0" : "\u25A1"}
                    </Text>
                    <View style={styles.metricInfo}>
                      <Text style={styles.metricName}>{metric.label}</Text>
                      <Text style={styles.metricDesc}>
                        {metric.description}
                      </Text>
                    </View>
                  </Pressable>
                );
              })}
            </View>
          )}

          {/* Separator */}
          <View style={styles.separator} />

          {/* Multiple runs */}
          <Text style={styles.label}>Multiple Runs</Text>
          <View style={styles.counterRow}>
            <Pressable onPress={decRuns} style={styles.counterBtn}>
              <Text style={styles.counterBtnText}>-</Text>
            </Pressable>
            <Text style={styles.counterValue}>{multipleRuns}</Text>
            <Pressable onPress={incRuns} style={styles.counterBtn}>
              <Text style={styles.counterBtnText}>+</Text>
            </Pressable>
          </View>

          {/* Track convergence */}
          <View style={styles.toggleRow}>
            <Text style={styles.label}>Track Convergence</Text>
            <Switch
              value={trackConvergence}
              onValueChange={setTrackConvergence}
              trackColor={{
                false: colors.text.tertiary,
                true: colors.accent.base,
              }}
              thumbColor={colors.text.primary}
            />
          </View>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  section: {
    marginBottom: spacing.lg,
  },
  chipRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: spacing.md,
  },
  chip: {
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 8,
    paddingVertical: 6,
    paddingHorizontal: 12,
  },
  chipActive: {
    backgroundColor: "#6366f1",
    borderColor: "#6366f1",
  },
  chipText: {
    fontSize: 13,
    color: "#94a3b8",
  },
  chipTextActive: {
    color: "#ffffff",
  },
  label: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.text.primary,
    marginBottom: spacing.xs,
  },
  modeRow: {
    flexDirection: "row",
    gap: 6,
    marginBottom: spacing.md,
  },
  modeChip: {
    flex: 1,
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 8,
    paddingVertical: 8,
    alignItems: "center",
  },
  metricsList: {
    marginBottom: spacing.md,
  },
  metricRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    paddingVertical: 6,
  },
  checkbox: {
    fontSize: 18,
    color: "#64748b",
    marginRight: spacing.sm,
    lineHeight: 20,
  },
  checkboxActive: {
    color: "#6366f1",
  },
  metricInfo: {
    flex: 1,
  },
  metricName: {
    fontSize: 13,
    fontWeight: "600",
    color: colors.text.primary,
  },
  metricDesc: {
    fontSize: 11,
    color: colors.text.tertiary,
    marginTop: 2,
  },
  separator: {
    height: 1,
    backgroundColor: "#334155",
    marginVertical: spacing.md,
  },
  counterRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  counterBtn: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
    alignItems: "center",
    justifyContent: "center",
  },
  counterBtnText: {
    fontSize: 18,
    color: colors.text.primary,
    fontWeight: "600",
  },
  counterValue: {
    fontSize: 16,
    fontWeight: "600",
    color: colors.text.primary,
    minWidth: 48,
    textAlign: "center",
    fontFamily: "SpaceMono",
  },
  toggleRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.md,
  },
});
