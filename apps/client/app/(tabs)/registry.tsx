import React, { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, Alert, FlatList, View } from "react-native";
import { router } from "expo-router";

import { Text, chrome } from "@/src/design";
import ExperimentCard from "@/src/components/ExperimentCard";
import {
  getDefaultConfig,
  listExperiments,
  runExperiment,
} from "@/src/lib/api";
import type { ExperimentConfig, RegistryEntry } from "@/src/lib/types";

export default function RegistryScreen() {
  const [experiments, setExperiments] = useState<RegistryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listExperiments();
      setExperiments(data);
    } catch (err) {
      Alert.alert("Error", err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleRun = async (name: string) => {
    setRunning(name);
    try {
      const raw = await getDefaultConfig(name);
      // Disable visualization for API runs
      const config = { ...raw, visualization_type: "none" } as unknown as ExperimentConfig;
      const result = await runExperiment(config);
      Alert.alert(
        "Experiment Complete",
        `${name} finished with ${result.analysis.measurement_results.unique_outcomes} unique outcomes`,
      );
    } catch (err) {
      Alert.alert("Run Failed", err instanceof Error ? err.message : String(err));
    } finally {
      setRunning(null);
    }
  };

  const handleCustomize = async (name: string) => {
    // Navigate to Configure tab — in a real app this would pre-fill the config
    router.navigate("/(tabs)/configure");
  };

  if (loading) {
    return (
      <View className="flex-1 items-center justify-center bg-base">
        <ActivityIndicator size="large" color={chrome.accent.base} />
      </View>
    );
  }

  return (
    <FlatList
      className="flex-1 bg-base"
      contentContainerStyle={{ padding: 16, paddingBottom: 80 }}
      data={experiments}
      keyExtractor={(item) => item.name}
      onRefresh={refresh}
      refreshing={loading}
      ListHeaderComponent={
        <Text
          variant="bodyLg"
          weight="semibold"
          tone="secondary"
          className="mb-md uppercase"
          style={{ letterSpacing: 0.5 }}
        >
          {experiments.length} Experiment{experiments.length !== 1 ? "s" : ""}
        </Text>
      }
      renderItem={({ item }) => (
        <View>
          <ExperimentCard
            name={item.name}
            description={item.description}
            onRun={() => handleRun(item.name)}
            onCustomize={() => handleCustomize(item.name)}
          />
          {running === item.name && (
            <ActivityIndicator
              style={{ position: "absolute", right: 16, top: 16 }}
              size="small"
              color={chrome.accent.base}
            />
          )}
        </View>
      )}
    />
  );
}
