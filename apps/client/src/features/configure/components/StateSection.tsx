import React from "react";
import { View } from "react-native";

import { Chip, Text } from "@/src/design";
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
    <View className="mb-lg">
      <SectionHeader title="State Type" onInfo={onInfo} />

      <View className="mb-md flex-row flex-wrap" style={{ gap: 6 }}>
        {STATE_TYPES.map((st) => {
          const active = stateType === st.id;
          return (
            <Chip
              key={st.id}
              label={st.label}
              tone={active ? "accent" : "neutral"}
              selected={active}
              onPress={() => setStateType(st.id as StateType)}
            />
          );
        })}
      </View>

      {isBell && (
        <Text variant="body" tone="accent" className="mb-sm">
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
