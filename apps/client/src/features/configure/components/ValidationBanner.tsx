import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors, spacing, radii } from "@/src/theme";
import type { ConfigWarning } from "../useExperimentConfig";

interface ValidationBannerProps {
  warnings: ConfigWarning[];
}

const LEVEL_STYLES: Record<
  ConfigWarning["level"],
  { background: string; border: string; icon: string }
> = {
  error: {
    background: "rgba(239, 68, 68, 0.12)",
    border: colors.status.error,
    icon: "!",
  },
  warning: {
    background: "rgba(245, 158, 11, 0.12)",
    border: colors.status.warning,
    icon: "!",
  },
  info: {
    background: "rgba(99, 102, 241, 0.08)",
    border: colors.status.info,
    icon: "i",
  },
};

export function ValidationBanner({ warnings }: ValidationBannerProps) {
  if (warnings.length === 0) {
    return null;
  }

  return (
    <View style={styles.container}>
      {warnings.map((w, idx) => {
        const level = LEVEL_STYLES[w.level];
        return (
          <View
            key={idx}
            style={[
              styles.banner,
              {
                backgroundColor: level.background,
                borderLeftColor: level.border,
              },
            ]}
          >
            <View
              style={[styles.iconCircle, { borderColor: level.border }]}
            >
              <Text style={[styles.iconText, { color: level.border }]}>
                {level.icon}
              </Text>
            </View>
            <Text style={styles.message}>{w.message}</Text>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: spacing.md,
    gap: 6,
  },
  banner: {
    flexDirection: "row",
    alignItems: "center",
    borderLeftWidth: 4,
    borderRadius: radii.sm,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  iconCircle: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 1,
    alignItems: "center",
    justifyContent: "center",
    marginRight: spacing.sm,
  },
  iconText: {
    fontSize: 10,
    fontWeight: "700",
  },
  message: {
    fontSize: 12,
    color: colors.text.primary,
    flex: 1,
  },
});
