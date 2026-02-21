import React from "react";
import { StyleSheet, Text, View } from "react-native";

interface Props {
  name: string;
  value: number | null | undefined;
  /** Short description shown below the value */
  subtitle?: string;
  /** Optional color for the value text */
  color?: string;
}

export default function MetricCard({ name, value, subtitle, color }: Props) {
  const displayValue =
    value == null ? "N/A" : typeof value === "number" ? value.toFixed(4) : "—";

  return (
    <View style={styles.card}>
      <Text style={styles.name}>{name}</Text>
      <Text style={[styles.value, color ? { color } : undefined]}>
        {displayValue}
      </Text>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}

      {/* Interpretation bar */}
      {value != null && typeof value === "number" && (
        <View style={styles.barTrack}>
          <View
            style={[
              styles.barFill,
              { width: `${Math.min(Math.abs(value) * 100, 100)}%` },
            ]}
          />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#334155",
  },
  name: {
    color: "#94a3b8",
    fontSize: 12,
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  value: {
    color: "#e2e8f0",
    fontSize: 28,
    fontWeight: "700",
    fontFamily: "SpaceMono",
  },
  subtitle: { color: "#64748b", fontSize: 12, marginTop: 4 },
  barTrack: {
    height: 4,
    backgroundColor: "#334155",
    borderRadius: 2,
    marginTop: 12,
    overflow: "hidden",
  },
  barFill: {
    height: 4,
    backgroundColor: "#6366f1",
    borderRadius: 2,
  },
});
