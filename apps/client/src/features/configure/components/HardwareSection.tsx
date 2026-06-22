import React, { useState } from "react";
import { View, Text, Pressable, TextInput, Switch, StyleSheet, ActivityIndicator } from "react-native";
import { colors, spacing } from "@/src/theme";
import type { HardwareBackend } from "@/src/lib/api";
import { OPTIMIZATION_LEVELS } from "../constants";
import { SectionHeader } from "./SectionHeader";

interface HardwareSectionProps {
  backendName: string;
  setBackendName: (v: string) => void;
  optimizationLevel: number;
  setOptimizationLevel: (v: number) => void;
  hardwareSession: boolean;
  setHardwareSession: (v: boolean) => void;
  onInfo: () => void;
  /** Live backends from the backend API (single source of truth). */
  backends: HardwareBackend[];
  backendsAvailable: boolean;
  backendsReason: string | null;
  backendsLoading: boolean;
}

export function HardwareSection({
  backendName,
  setBackendName,
  optimizationLevel,
  setOptimizationLevel,
  hardwareSession,
  setHardwareSession,
  onInfo,
  backends,
  backendsAvailable,
  backendsReason,
  backendsLoading,
}: HardwareSectionProps) {
  const backendNames = backends
    .map((b) => b.name)
    .filter((n): n is string => !!n);
  const isKnownBackend = backendNames.includes(backendName);
  // When the live list is unavailable, manual entry is the only path.
  const [showCustom, setShowCustom] = useState(
    !backendsAvailable || (!isKnownBackend && backendName !== ""),
  );

  const selectedOptLevel = OPTIMIZATION_LEVELS.find(
    (o) => o.level === optimizationLevel,
  );

  return (
    <View style={styles.section}>
      <SectionHeader title="Hardware" onInfo={onInfo} />

      {/* Backend selection */}
      <Text style={styles.label}>Backend</Text>

      {backendsLoading && (
        <View style={styles.loadingRow}>
          <ActivityIndicator size="small" color={colors.accent.base} />
          <Text style={styles.helperText}>Loading backends…</Text>
        </View>
      )}

      {!backendsLoading && !backendsAvailable && (
        <View style={styles.noticeBox}>
          <Text style={styles.noticeText}>
            No live backends.{" "}
            {backendsReason ?? "IBM Quantum credentials are not configured."}
          </Text>
          <Text style={styles.noticeSubText}>
            Enter a backend name manually below (offline — not verified against a
            real device).
          </Text>
        </View>
      )}

      {backendsAvailable && (
        <View style={styles.chipRow}>
          {backendNames.map((name) => {
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
      )}

      {(showCustom || !backendsAvailable) && (
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
  loadingRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: spacing.md,
  },
  noticeBox: {
    backgroundColor: "rgba(245, 158, 11, 0.10)",
    borderWidth: 1,
    borderColor: colors.status.warning,
    borderRadius: 8,
    padding: 10,
    marginBottom: spacing.md,
  },
  noticeText: {
    fontSize: 12,
    color: colors.text.primary,
    fontWeight: "600",
  },
  noticeSubText: {
    fontSize: 11,
    color: colors.text.tertiary,
    marginTop: 4,
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
