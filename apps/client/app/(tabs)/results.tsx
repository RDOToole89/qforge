import React, { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, FlatList, Pressable, View } from "react-native";

import { Button, Stack, Text, chrome } from "@/src/design";
import { listResults } from "@/src/lib/api";
import type { StoredResultEntry } from "@/src/lib/types";

export default function ResultsScreen() {
  const [entries, setEntries] = useState<StoredResultEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listResults();
      setEntries(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  if (loading) {
    return (
      <View className="flex-1 items-center justify-center bg-base p-2xl">
        <ActivityIndicator size="large" color={chrome.accent.base} />
      </View>
    );
  }

  if (error) {
    return (
      <View className="flex-1 items-center justify-center bg-base p-2xl">
        <Text variant="label" tone="error" className="mb-md text-center">
          {error}
        </Text>
        <Button variant="primary" size="md" onPress={refresh}>
          Retry
        </Button>
      </View>
    );
  }

  if (entries.length === 0) {
    return (
      <View className="flex-1 items-center justify-center bg-base p-2xl">
        <Text variant="headingSm" weight="semibold" tone="secondary">
          No results yet
        </Text>
        <Text variant="bodyLg" tone="tertiary" className="mt-xs">
          Run an experiment from the Configure tab
        </Text>
      </View>
    );
  }

  return (
    <FlatList
      className="flex-1 bg-base"
      contentContainerStyle={{ padding: 16 }}
      data={entries}
      keyExtractor={(item) => item.filename}
      onRefresh={refresh}
      refreshing={loading}
      renderItem={({ item }) => <ResultRow entry={item} />}
    />
  );
}

function ResultRow({ entry }: { entry: StoredResultEntry }) {
  const sizeKB = entry.size_bytes
    ? `${(entry.size_bytes / 1024).toFixed(1)} KB`
    : "";
  const date = entry.modified
    ? new Date(entry.modified * 1000).toLocaleString()
    : "";

  return (
    <Pressable
      className="flex-row justify-between rounded-lg border border-default bg-surface"
      style={({ pressed }) => [
        { padding: 14, marginBottom: 10 },
        pressed && { opacity: 0.7 },
      ]}
    >
      <Stack className="flex-1">
        <Text variant="label" weight="semibold" mono numberOfLines={1}>
          {entry.experiment_id ?? entry.filename}
        </Text>
        <Text variant="body" tone="secondary" className="mt-xs">
          {[entry.state_type, entry.num_qubits && `${entry.num_qubits}q`]
            .filter(Boolean)
            .join(" · ")}
        </Text>
      </Stack>
      <Stack align="end" className="ml-md">
        <Text variant="bodySm" tone="tertiary">
          {date}
        </Text>
        <Text variant="bodySm" tone="tertiary" style={{ marginTop: 2 }}>
          {sizeKB}
        </Text>
      </Stack>
    </Pressable>
  );
}
