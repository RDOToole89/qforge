import React from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";

interface Props {
  /** Measurement counts: { "000": 420, "111": 380, ... } */
  counts: Record<string, number>;
  /** Max number of outcomes to display */
  topN?: number;
}

/**
 * Horizontal bar chart showing top-N measurement outcomes.
 * Pure RN — no charting library required.
 */
export default function ResultChart({ counts, topN = 16 }: Props) {
  const sorted = Object.entries(counts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, topN);

  if (sorted.length === 0) return null;

  const maxCount = sorted[0][1];
  const total = Object.values(counts).reduce((s, v) => s + v, 0);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Measurement Distribution</Text>
      <ScrollView style={styles.scroll}>
        {sorted.map(([bitstring, count]) => {
          const pct = total > 0 ? ((count / total) * 100).toFixed(1) : "0";
          const width = maxCount > 0 ? (count / maxCount) * 100 : 0;

          return (
            <View key={bitstring} style={styles.row}>
              <Text style={styles.label}>|{bitstring}⟩</Text>
              <View style={styles.barContainer}>
                <View style={[styles.bar, { width: `${width}%` }]} />
              </View>
              <Text style={styles.count}>
                {count} ({pct}%)
              </Text>
            </View>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: "#334155",
  },
  title: {
    color: "#e2e8f0",
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 12,
  },
  scroll: { maxHeight: 400 },
  row: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  label: {
    color: "#a5b4fc",
    fontSize: 13,
    fontFamily: "SpaceMono",
    width: 90,
  },
  barContainer: {
    flex: 1,
    height: 18,
    backgroundColor: "#0f172a",
    borderRadius: 4,
    overflow: "hidden",
    marginHorizontal: 8,
  },
  bar: {
    height: 18,
    backgroundColor: "#6366f1",
    borderRadius: 4,
  },
  count: {
    color: "#94a3b8",
    fontSize: 12,
    fontFamily: "SpaceMono",
    width: 85,
    textAlign: "right",
  },
});
