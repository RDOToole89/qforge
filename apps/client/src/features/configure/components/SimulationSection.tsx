import React from "react";
import { StyleSheet, TextInput, View } from "react-native";

import { Chip, Text, chrome } from "@/src/design";
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
    <View className="mb-lg">
      <SectionHeader title="Simulation" onInfo={onInfo} />

      {/* Sim mode chips */}
      <View className="mb-md flex-row flex-wrap" style={{ gap: 6 }}>
        {SIM_MODES.map((mode) => {
          const active = simMode === mode.id;
          return (
            <Chip
              key={mode.id}
              label={mode.label}
              tone={active ? "accent" : "neutral"}
              selected={active}
              onPress={() => setSimMode(mode.id as SimMode)}
            />
          );
        })}
      </View>

      {/* Shot presets */}
      <Text variant="label" weight="semibold" className="mb-xs">
        Shots
      </Text>
      <View className="mb-md flex-row flex-wrap" style={{ gap: 6 }}>
        {SHOT_PRESETS.map((preset) => {
          const active = shots === preset;
          return (
            <Chip
              key={preset}
              label={formatShots(preset)}
              tone={active ? "accent" : "neutral"}
              selected={active}
              onPress={() => setShots(preset)}
            />
          );
        })}
      </View>

      {/* RNG Seed */}
      <Text variant="label" weight="semibold" className="mb-xs">
        RNG Seed
        <Text variant="body" tone="secondary">
          {" "}
          (deterministic reproducibility)
        </Text>
      </Text>
      <TextInput
        style={[styles.textInput, showHardwareSection && styles.inputDisabled]}
        keyboardType="numeric"
        placeholder={
          showHardwareSection
            ? "Not available in hardware mode"
            : "Optional (for reproducibility)"
        }
        placeholderTextColor={chrome.text.tertiary}
        value={rngSeed !== null ? String(rngSeed) : ""}
        onChangeText={handleSeedChange}
        editable={!showHardwareSection}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  textInput: {
    backgroundColor: chrome.bg.surface,
    borderWidth: 1,
    borderColor: chrome.border.default,
    borderRadius: 8,
    padding: 10,
    color: chrome.text.primary,
    fontSize: 13,
    marginBottom: 12,
  },
  inputDisabled: {
    opacity: 0.4,
  },
});
