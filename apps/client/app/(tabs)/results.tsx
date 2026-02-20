import React, { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";

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
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6366f1" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error}</Text>
        <Pressable style={styles.retryBtn} onPress={refresh}>
          <Text style={styles.retryText}>Retry</Text>
        </Pressable>
      </View>
    );
  }

  if (entries.length === 0) {
    return (
      <View style={styles.center}>
        <Text style={styles.emptyText}>No results yet</Text>
        <Text style={styles.emptySubtext}>
          Run an experiment from the Configure tab
        </Text>
      </View>
    );
  }

  return (
    <FlatList
      style={styles.screen}
      contentContainerStyle={styles.list}
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
    <Pressable style={({ pressed }) => [styles.row, pressed && styles.pressed]}>
      <View style={styles.rowMain}>
        <Text style={styles.rowId} numberOfLines={1}>
          {entry.experiment_id ?? entry.filename}
        </Text>
        <Text style={styles.rowMeta}>
          {[entry.state_type, entry.num_qubits && `${entry.num_qubits}q`]
            .filter(Boolean)
            .join(" · ")}
        </Text>
      </View>
      <View style={styles.rowRight}>
        <Text style={styles.rowDate}>{date}</Text>
        <Text style={styles.rowSize}>{sizeKB}</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#0f172a" },
  list: { padding: 16 },
  center: {
    flex: 1,
    backgroundColor: "#0f172a",
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },

  row: {
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    flexDirection: "row",
    justifyContent: "space-between",
    borderWidth: 1,
    borderColor: "#334155",
  },
  pressed: { opacity: 0.7 },
  rowMain: { flex: 1 },
  rowId: { color: "#e2e8f0", fontSize: 14, fontWeight: "600", fontFamily: "SpaceMono" },
  rowMeta: { color: "#94a3b8", fontSize: 12, marginTop: 4 },
  rowRight: { alignItems: "flex-end", marginLeft: 12 },
  rowDate: { color: "#64748b", fontSize: 11 },
  rowSize: { color: "#475569", fontSize: 11, marginTop: 2 },

  errorText: { color: "#f87171", fontSize: 14, textAlign: "center", marginBottom: 12 },
  retryBtn: {
    backgroundColor: "#6366f1",
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 24,
  },
  retryText: { color: "#fff", fontWeight: "600" },

  emptyText: { color: "#94a3b8", fontSize: 16, fontWeight: "600" },
  emptySubtext: { color: "#64748b", fontSize: 13, marginTop: 4 },
});
