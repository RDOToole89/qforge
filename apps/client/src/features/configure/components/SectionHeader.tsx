import React from "react";
import { View, Text, Pressable, Switch, StyleSheet } from "react-native";
import { colors, spacing } from "@/src/theme";

interface SectionHeaderProps {
  title: string;
  onInfo?: () => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  switchValue?: boolean;
  onSwitchChange?: (v: boolean) => void;
  disabled?: boolean;
}

export function SectionHeader({
  title,
  onInfo,
  collapsed,
  onToggleCollapse,
  switchValue,
  onSwitchChange,
  disabled = false,
}: SectionHeaderProps) {
  return (
    <View style={[styles.container, disabled && styles.disabled]}>
      <Text style={[styles.title, disabled && styles.disabledText]}>
        {title}
      </Text>

      {onInfo != null && (
        <Pressable
          onPress={onInfo}
          style={styles.infoButton}
          hitSlop={8}
          disabled={disabled}
        >
          <Text style={styles.infoIcon}>i</Text>
        </Pressable>
      )}

      <View style={styles.spacer} />

      {switchValue != null && onSwitchChange != null && (
        <Switch
          value={switchValue}
          onValueChange={onSwitchChange}
          disabled={disabled}
          trackColor={{
            false: colors.text.tertiary,
            true: colors.accent.base,
          }}
          thumbColor={colors.text.primary}
        />
      )}

      {collapsed != null && onToggleCollapse != null && (
        <Pressable
          onPress={onToggleCollapse}
          hitSlop={8}
          disabled={disabled}
        >
          <Text style={[styles.chevron, disabled && styles.disabledText]}>
            {collapsed ? "\u25B8" : "\u25BE"}
          </Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  disabled: {
    opacity: 0.5,
  },
  title: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.text.primary,
  },
  disabledText: {
    color: colors.text.tertiary,
  },
  infoButton: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.text.tertiary,
    alignItems: "center",
    justifyContent: "center",
    marginLeft: spacing.sm,
  },
  infoIcon: {
    fontSize: 11,
    color: colors.text.secondary,
    fontWeight: "600",
  },
  spacer: {
    flex: 1,
  },
  chevron: {
    fontSize: 16,
    color: colors.text.secondary,
    marginLeft: spacing.sm,
  },
});
