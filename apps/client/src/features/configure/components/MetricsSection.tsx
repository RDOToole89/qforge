import React from "react";
import { Pressable, Switch, View } from "react-native";

import { Chip, Row, SegmentedControl, Text, chrome } from "@/src/design";
import type { ExperimentType } from "@/src/lib/types";
import {
  EXPERIMENT_TYPES,
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
  experimentType: ExperimentType | null;
  setExperimentType: (v: ExperimentType | null) => void;
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
  experimentType,
  setExperimentType,
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
    <View className="mb-lg">
      <SectionHeader
        title="Analysis Metrics"
        switchValue={metricsEnabled}
        onSwitchChange={setMetricsEnabled}
        collapsed={collapsed}
        onToggleCollapse={onToggleCollapse}
        onInfo={onInfo}
      />

      {metricsEnabled && !collapsed && (
        <>
          {/* Experiment type */}
          <Text variant="label" weight="semibold" className="mb-xs">
            Experiment Type
          </Text>
          <View className="mb-md flex-row flex-wrap" style={{ gap: 6 }}>
            {EXPERIMENT_TYPES.map((rt) => {
              const active = experimentType === rt.id;
              return (
                <Chip
                  key={rt.id}
                  label={rt.label}
                  tone={active ? "accent" : "neutral"}
                  selected={active}
                  onPress={() =>
                    setExperimentType(active ? null : (rt.id as ExperimentType))
                  }
                />
              );
            })}
          </View>

          {/* Metrics mode segmented control */}
          <Text variant="label" weight="semibold" className="mb-xs">
            Metrics Selection
          </Text>
          <SegmentedControl<"profile" | "individual">
            className="mb-md"
            value={metricsMode}
            onChange={setMetricsMode}
            options={[
              { label: "Profile", value: "profile" },
              { label: "Individual", value: "individual" },
            ]}
          />

          {/* Profile mode */}
          {metricsMode === "profile" && (
            <View className="mb-md flex-row flex-wrap" style={{ gap: 6 }}>
              {METRIC_PROFILES.map((profile) => {
                const active = selectedProfile === profile.id;
                return (
                  <Chip
                    key={profile.id}
                    label={`${profile.label} (${profile.metrics.length} metrics)`}
                    tone={active ? "accent" : "neutral"}
                    selected={active}
                    onPress={() => setSelectedProfile(profile.id)}
                  />
                );
              })}
            </View>
          )}

          {/* Individual mode */}
          {metricsMode === "individual" && (
            <View className="mb-md">
              {INDIVIDUAL_METRICS.map((metric) => {
                const checked = selectedMetrics.includes(metric.id);
                return (
                  <Pressable
                    key={metric.id}
                    onPress={() => toggleMetric(metric.id)}
                    className="flex-row items-start"
                    style={{ paddingVertical: 6 }}
                  >
                    <Text
                      tone={checked ? "accent" : "tertiary"}
                      className="mr-sm"
                      style={{ fontSize: 18, lineHeight: 20 }}
                    >
                      {checked ? "■" : "□"}
                    </Text>
                    <View className="flex-1">
                      <Text variant="bodyLg" weight="semibold">
                        {metric.label}
                      </Text>
                      <Text variant="bodySm" tone="tertiary" style={{ marginTop: 2 }}>
                        {metric.description}
                      </Text>
                    </View>
                  </Pressable>
                );
              })}
            </View>
          )}

          {/* Separator */}
          <View className="my-md h-px bg-default" />

          {/* Multiple runs */}
          <Text variant="label" weight="semibold" className="mb-xs">
            Multiple Runs
          </Text>
          <Row align="center" className="mb-md">
            <Pressable
              onPress={decRuns}
              className="items-center justify-center rounded-md border border-default bg-surface"
              style={{ width: 36, height: 36 }}
            >
              <Text variant="heading" weight="semibold">
                -
              </Text>
            </Pressable>
            <Text
              variant="headingSm"
              weight="semibold"
              mono
              className="text-center"
              style={{ minWidth: 48 }}
            >
              {multipleRuns}
            </Text>
            <Pressable
              onPress={incRuns}
              className="items-center justify-center rounded-md border border-default bg-surface"
              style={{ width: 36, height: 36 }}
            >
              <Text variant="heading" weight="semibold">
                +
              </Text>
            </Pressable>
          </Row>

          {/* Track convergence */}
          <Row align="center" justify="between" className="mb-md">
            <Text variant="label" weight="semibold">
              Track Convergence
            </Text>
            <Switch
              value={trackConvergence}
              onValueChange={setTrackConvergence}
              trackColor={{
                false: chrome.text.tertiary,
                true: chrome.accent.base,
              }}
              thumbColor={chrome.text.primary}
            />
          </Row>
        </>
      )}
    </View>
  );
}
