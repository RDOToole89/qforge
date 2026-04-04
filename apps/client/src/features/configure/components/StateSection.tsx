import React from "react";
import { View, Text, Pressable, StyleSheet } from "react-native";
import { colors, spacing } from "@/src/theme";
import { STATE_TYPES } from "../constants";
import { SectionHeader } from "./SectionHeader";
import ConfigSlider from "@/src/components/ConfigSlider";
import type { StateType } from "@/src/lib/types";

interface StateSectionProps {
  stateType: StateType;
  setStateType: (v: StateType) => void;
  numQubits: number;
  setNumQubits: (v: number) => void;
  onInfo: () => void;
}

export function StateSection({
  stateType,
  setStateType,
  numQubits,
  setNumQubits,
  onInfo,
}: StateSectionProps) {
  const isBell = stateType === "BELL";

  return (
    <View style={styles.section}>
      <SectionHeader title="State Type" onInfo={onInfo} />

      <View style={styles.chipRow}>
        {STATE_TYPES.map((st) => {
          const active = stateType === st.id;
          return (
            <Pressable
              key={st.id}
              onPress={() => setStateType(st.id as StateType)}
              style={[styles.chip, active && styles.chipActive]}
            >
              <Text style={[styles.chipText, active && styles.chipTextActive]}>
                {st.label}
              </Text>
            </Pressable>
          );
        })}
      </View>

      {isBell && (
        <Text style={styles.infoText}>
          Bell states are strictly 2-qubit.
        </Text>
      )}

      <ConfigSlider
        label="Qubits"
        value={numQubits}
        min={1}
        max={20}
        step={1}
        onValueChange={(v) => setNumQubits(Math.round(v))}
        disabled={isBell}
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
  infoText: {
    fontSize: 12,
    color: colors.status.info,
    marginBottom: spacing.sm,
  },
});
