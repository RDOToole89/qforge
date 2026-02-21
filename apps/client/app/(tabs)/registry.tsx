import React, { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  FlatList,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { router } from "expo-router";

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
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6366f1" />
      </View>
    );
  }

  return (
    <FlatList
      style={styles.screen}
      contentContainerStyle={styles.list}
      data={experiments}
      keyExtractor={(item) => item.name}
      onRefresh={refresh}
      refreshing={loading}
      ListHeaderComponent={
        <Text style={styles.header}>
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
              style={styles.spinner}
              size="small"
              color="#6366f1"
            />
          )}
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#0f172a" },
  list: { padding: 16, paddingBottom: 80 },
  center: {
    flex: 1,
    backgroundColor: "#0f172a",
    justifyContent: "center",
    alignItems: "center",
  },
  header: {
    color: "#94a3b8",
    fontSize: 13,
    fontWeight: "600",
    marginBottom: 12,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  spinner: { position: "absolute", right: 16, top: 16 },
});
