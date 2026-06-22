import React from "react";
import { StyleSheet, View } from "react-native";

import { Card, Text, chrome, radii, spacing } from "@/src/design";

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
    <Card variant="elevated" padding="lg" className="mb-md">
      <Text
        variant="body"
        tone="secondary"
        weight="semibold"
        className="uppercase mb-xs"
        style={styles.nameSpacing}
      >
        {name}
      </Text>
      <Text
        variant="display"
        weight="bold"
        mono
        tone="primary"
        style={color ? { color } : undefined}
      >
        {displayValue}
      </Text>
      {subtitle ? (
        <Text variant="body" tone="tertiary" className="mt-xs">
          {subtitle}
        </Text>
      ) : null}

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
    </Card>
  );
}

const styles = StyleSheet.create({
  nameSpacing: { letterSpacing: 0.5 },
  barTrack: {
    height: 4,
    backgroundColor: chrome.border.default,
    borderRadius: radii.xs,
    marginTop: spacing.md,
    overflow: "hidden",
  },
  barFill: {
    height: 4,
    backgroundColor: chrome.accent.base,
    borderRadius: radii.xs,
  },
});
