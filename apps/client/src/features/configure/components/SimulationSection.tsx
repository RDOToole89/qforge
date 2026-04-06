import React from "react";
import { View, Text, Pressable, TextInput, StyleSheet } from "react-native";
import { colors, spacing } from "@/src/theme";
import { SIM_MODES, SHOT_PRESETS } from "../constants";
import { SectionHeader } from "./SectionHeader";
import type { SimMode } from "@/src/lib/types";

interface SimulationSectionProps {
  simMode: SimMode;
  setSimMode: (v: SimMode) => void;
  shots: number;
  setShots: (v: number) => void;
  rngSeed: number | null;
  setRngSeed: (v: number | null) => void;
  showHardwareSection: boolean;
  onInfo: () => void;
}

function formatShots(n: number): string {
  return `${(n / 1000).toFixed(3)}k`;
}

export function SimulationSection({
  simMode,
  setSimMode,
  shots,
  setShots,
  rngSeed,
  setRngSeed,
  showHardwareSection,
  onInfo,
}: SimulationSectionProps) {
  const handleSeedChange = (text: string) => {
    if (text === "") {
      setRngSeed(null);
      return;
    }
    const num = parseInt(text, 10);
    if (!isNaN(num)) {
      setRngSeed(num);
    }
  };

  return (
    <View style={styles.section}>
      <SectionHeader title="Simulation" onInfo={onInfo} />

      {/* Sim mode chips */}
      <View style={styles.chipRow}>
        {SIM_MODES.map((mode) => {
          const active = simMode === mode.id;
          return (
            <Pressable
              key={mode.id}
              onPress={() => setSimMode(mode.id as SimMode)}
              style={[styles.chip, active && styles.chipActive]}
            >
              <Text style={[styles.chipText, active && styles.chipTextActive]}>
                {mode.label}
              </Text>
            </Pressable>
          );
        })}
      </View>

      {/* Shot presets */}
      <Text style={styles.label}>Shots</Text>
      <View style={styles.chipRow}>
        {SHOT_PRESETS.map((preset) => {
          const active = shots === preset;
          return (
            <Pressable
              key={preset}
              onPress={() => setShots(preset)}
              style={[styles.chip, active && styles.chipActive]}
            >
              <Text style={[styles.chipText, active && styles.chipTextActive]}>
                {formatShots(preset)}
              </Text>
            </Pressable>
          );
        })}
      </View>

      {/* RNG Seed */}
      <Text style={styles.label}>
        RNG Seed
        <Text style={styles.secondaryText}> (deterministic reproducibility)</Text>
      </Text>
      <TextInput
        style={[styles.textInput, showHardwareSection && styles.inputDisabled]}
        keyboardType="numeric"
        placeholder={
          showHardwareSection
            ? "Not available in hardware mode"
            : "Optional (for reproducibility)"
        }
        placeholderTextColor={colors.text.tertiary}
        value={rngSeed !== null ? String(rngSeed) : ""}
        onChangeText={handleSeedChange}
        editable={!showHardwareSection}
      />
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
  secondaryText: {
    fontSize: 12,
    fontWeight: "400",
    color: colors.text.secondary,
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
  inputDisabled: {
    opacity: 0.4,
  },
});
