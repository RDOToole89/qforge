import React, { useState } from "react";
import { View, Text, Pressable, TextInput, Switch, StyleSheet } from "react-native";
import { colors, spacing } from "@/src/theme";
import { KNOWN_BACKENDS, OPTIMIZATION_LEVELS } from "../constants";
import { SectionHeader } from "./SectionHeader";

interface HardwareSectionProps {
  backendName: string;
  setBackendName: (v: string) => void;
  optimizationLevel: number;
  setOptimizationLevel: (v: number) => void;
  hardwareSession: boolean;
  setHardwareSession: (v: boolean) => void;
  onInfo: () => void;
}

export function HardwareSection({
  backendName,
  setBackendName,
  optimizationLevel,
  setOptimizationLevel,
  hardwareSession,
  setHardwareSession,
  onInfo,
}: HardwareSectionProps) {
  const isKnownBackend = (KNOWN_BACKENDS as readonly string[]).includes(backendName);
  const [showCustom, setShowCustom] = useState(!isKnownBackend && backendName !== "");

  const selectedOptLevel = OPTIMIZATION_LEVELS.find(
    (o) => o.level === optimizationLevel,
  );

  return (
    <View style={styles.section}>
      <SectionHeader title="Hardware" onInfo={onInfo} />

      {/* Backend selection */}
      <Text style={styles.label}>Backend</Text>
      <View style={styles.chipRow}>
        {KNOWN_BACKENDS.map((name) => {
          const active = backendName === name && !showCustom;
          return (
            <Pressable
              key={name}
              onPress={() => {
                setBackendName(name);
                setShowCustom(false);
              }}
              style={[styles.chip, active && styles.chipActive]}
            >
              <Text style={[styles.chipText, active && styles.chipTextActive]}>
                {name}
              </Text>
            </Pressable>
          );
        })}
        <Pressable
          onPress={() => {
            setShowCustom(true);
            if (isKnownBackend) setBackendName("");
          }}
          style={[styles.chip, showCustom && styles.chipActive]}
        >
          <Text style={[styles.chipText, showCustom && styles.chipTextActive]}>
            Custom
          </Text>
        </Pressable>
      </View>

      {showCustom && (
        <TextInput
          style={styles.textInput}
          placeholder="Enter backend name"
          placeholderTextColor={colors.text.tertiary}
          value={isKnownBackend ? "" : backendName}
          onChangeText={setBackendName}
          autoCapitalize="none"
          autoCorrect={false}
        />
      )}

      {/* Optimization level */}
      <Text style={styles.label}>Optimization Level</Text>
      <View style={styles.chipRow}>
        {OPTIMIZATION_LEVELS.map((opt) => {
          const active = optimizationLevel === opt.level;
          return (
            <Pressable
              key={opt.level}
              onPress={() => setOptimizationLevel(opt.level)}
              style={[styles.chip, active && styles.chipActive]}
            >
              <Text style={[styles.chipText, active && styles.chipTextActive]}>
                {opt.level} - {opt.label}
              </Text>
            </Pressable>
          );
        })}
      </View>
      {selectedOptLevel && (
        <Text style={styles.helperText}>{selectedOptLevel.description}</Text>
      )}

      {/* Hardware session */}
      <View style={styles.toggleRow}>
        <View style={styles.toggleLabel}>
          <Text style={styles.label}>Hardware Session</Text>
          <Text style={styles.helperText}>
            Keep backend reserved across sweep jobs
          </Text>
        </View>
        <Switch
          value={hardwareSession}
          onValueChange={setHardwareSession}
          trackColor={{ false: colors.text.tertiary, true: colors.accent.base }}
          thumbColor={colors.text.primary}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  section: {
    marginBottom: spacing.lg,
  },
  chipRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: spacing.md,
  },
  chip: {
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 8,
    paddingVertical: 6,
    paddingHorizontal: 12,
  },
  chipActive: {
    backgroundColor: "#6366f1",
    borderColor: "#6366f1",
  },
  chipText: {
    fontSize: 13,
    color: "#94a3b8",
  },
  chipTextActive: {
    color: "#ffffff",
  },
  label: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.text.primary,
    marginBottom: spacing.xs,
  },
  textInput: {
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 8,
    padding: 10,
    color: "#e2e8f0",
    fontSize: 13,
    marginBottom: spacing.md,
  },
  helperText: {
    fontSize: 11,
    color: colors.text.tertiary,
    marginBottom: spacing.md,
  },
  toggleRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  toggleLabel: {
    flex: 1,
    marginRight: spacing.md,
  },
});
