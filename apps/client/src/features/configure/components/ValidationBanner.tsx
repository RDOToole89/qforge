import React from "react";
import { StyleSheet, View } from "react-native";

import { Row, Stack, Text, chrome } from "@/src/design";
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
    border: chrome.status.error,
    icon: "!",
  },
  warning: {
    background: "rgba(245, 158, 11, 0.12)",
    border: chrome.status.warning,
    icon: "!",
  },
  info: {
    background: "rgba(99, 102, 241, 0.08)",
    border: chrome.status.info,
    icon: "i",
  },
};

export function ValidationBanner({ warnings }: ValidationBannerProps) {
  if (warnings.length === 0) {
    return null;
  }

  return (
    <Stack className="mt-md" style={{ gap: 6 }}>
      {warnings.map((w, idx) => {
        const level = LEVEL_STYLES[w.level];
        return (
          <Row
            key={idx}
            align="center"
            className="rounded-md"
            style={[
              styles.banner,
              {
                backgroundColor: level.background,
                borderLeftColor: level.border,
              },
            ]}
          >
            <View
              className="mr-sm items-center justify-center rounded-pill"
              style={[styles.iconCircle, { borderColor: level.border }]}
            >
              <Text variant="caption" weight="bold" style={{ color: level.border }}>
                {level.icon}
              </Text>
            </View>
            <Text variant="body" className="flex-1">
              {w.message}
            </Text>
          </Row>
        );
      })}
    </Stack>
  );
}

const styles = StyleSheet.create({
  banner: {
    borderLeftWidth: 4,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  iconCircle: {
    width: 18,
    height: 18,
    borderWidth: 1,
  },
});
