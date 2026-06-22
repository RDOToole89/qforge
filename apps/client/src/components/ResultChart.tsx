import React from "react";
import { ScrollView, StyleSheet, View } from "react-native";

import { Text, chrome, radii, viz } from "@/src/design";

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
      <Text variant="headingSm" weight="bold" tone="primary" className="mb-md">
        Measurement Distribution
      </Text>
      <ScrollView style={styles.scroll}>
        {sorted.map(([bitstring, count]) => {
          const pct = total > 0 ? ((count / total) * 100).toFixed(1) : "0";
          const width = maxCount > 0 ? (count / maxCount) * 100 : 0;

          return (
            <View key={bitstring} style={styles.row}>
              <Text variant="bodyLg" mono style={styles.label}>
                |{bitstring}⟩
              </Text>
              <View style={styles.barContainer}>
                <View style={[styles.bar, { width: `${width}%` }]} />
              </View>
              <Text variant="body" tone="secondary" mono style={styles.count}>
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
    backgroundColor: chrome.bg.surface,
    borderRadius: radii.lg,
    padding: 16,
    borderWidth: 1,
    borderColor: chrome.border.default,
  },
  scroll: { maxHeight: 400 },
  row: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  label: {
    color: chrome.accent.light,
    width: 90,
  },
  barContainer: {
    flex: 1,
    height: 18,
    backgroundColor: chrome.bg.primary,
    borderRadius: radii.sm,
    overflow: "hidden",
    marginHorizontal: 8,
  },
  bar: {
    height: 18,
    backgroundColor: viz.series[0],
    borderRadius: radii.sm,
  },
  count: {
    width: 85,
    textAlign: "right",
  },
});
