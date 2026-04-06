import React from "react";
import { View, Text, Pressable, TextInput, Switch, StyleSheet } from "react-native";
import { colors, spacing, radii } from "@/src/theme";
import { NOISE_TYPES } from "../constants";
import { SectionHeader } from "./SectionHeader";
import ConfigSlider from "@/src/components/ConfigSlider";
import type { NoiseType } from "@/src/lib/types";

interface NoiseSectionProps {
  noiseEnabled: boolean;
  setNoiseEnabled: (v: boolean) => void;
  noiseType: NoiseType;
  setNoiseType: (v: NoiseType) => void;
  errorRate: number;
  setErrorRate: (v: number) => void;
  t1: number | null;
  setT1: (v: number | null) => void;
  t2: number | null;
  setT2: (v: number | null) => void;
  readoutErrorRate: number | null;
  setReadoutErrorRate: (v: number | null) => void;
  balanceCircuit: boolean;
  setBalanceCircuit: (v: boolean) => void;
  noiseDisabledReason: string | null;
  showThermalParams: boolean;
  onInfo: () => void;
}

export function NoiseSection({
  noiseEnabled,
  setNoiseEnabled,
  noiseType,
  setNoiseType,
  errorRate,
  setErrorRate,
  t1,
  setT1,
  t2,
  setT2,
  readoutErrorRate,
  setReadoutErrorRate,
  balanceCircuit,
  setBalanceCircuit,
  noiseDisabledReason,
  showThermalParams,
  onInfo,
}: NoiseSectionProps) {
  const handleT1Change = (text: string) => {
    if (text === "") { setT1(null); return; }
    const num = parseFloat(text);
    if (!isNaN(num)) setT1(num);
  };

  const handleT2Change = (text: string) => {
    if (text === "") { setT2(null); return; }
    const num = parseFloat(text);
    if (!isNaN(num)) setT2(num);
  };

  return (
    <View style={styles.section}>
      <SectionHeader
        title="Noise"
        switchValue={noiseEnabled}
        onSwitchChange={setNoiseEnabled}
        onInfo={onInfo}
        disabled={noiseDisabledReason !== null}
      />

      {/* Disabled reason banner */}
      {noiseDisabledReason !== null && (
        <View style={styles.infoBanner}>
          <View style={styles.infoBannerIcon}>
            <Text style={styles.infoBannerIconText}>i</Text>
          </View>
          <Text style={styles.infoBannerText}>{noiseDisabledReason}</Text>
        </View>
      )}

      {/* Noise type + error rate (only when enabled) */}
      {noiseEnabled && (
        <>
          <Text style={styles.label}>Noise Type</Text>
          <View style={styles.chipRow}>
            {NOISE_TYPES.map((nt) => {
              const active = noiseType === nt.id;
              return (
                <Pressable
                  key={nt.id}
                  onPress={() => setNoiseType(nt.id as NoiseType)}
                  style={[styles.chip, active && styles.chipActive]}
                >
                  <Text
                    style={[styles.chipText, active && styles.chipTextActive]}
                  >
                    {nt.label}
                  </Text>
                </Pressable>
              );
            })}
          </View>

          <ConfigSlider
            label="Error Rate"
            value={errorRate}
            min={0}
            max={0.5}
            step={0.01}
            onValueChange={setErrorRate}
            formatValue={(v) => v.toFixed(2)}
          />

          {/* Thermal relaxation T1/T2 params */}
          {showThermalParams && (
            <>
              <View style={styles.thermalRow}>
                <View style={styles.thermalField}>
                  <Text style={styles.label}>T1</Text>
                  <View style={styles.inputWithUnit}>
                    <TextInput
                      style={styles.textInput}
                      keyboardType="numeric"
                      placeholder="100"
                      placeholderTextColor={colors.text.tertiary}
                      value={t1 !== null ? String(t1) : ""}
                      onChangeText={handleT1Change}
                    />
                    <Text style={styles.unitLabel}>us</Text>
                  </View>
                </View>
                <View style={styles.thermalField}>
                  <Text style={styles.label}>T2</Text>
                  <View style={styles.inputWithUnit}>
                    <TextInput
                      style={styles.textInput}
                      keyboardType="numeric"
                      placeholder="80"
                      placeholderTextColor={colors.text.tertiary}
                      value={t2 !== null ? String(t2) : ""}
                      onChangeText={handleT2Change}
                    />
                    <Text style={styles.unitLabel}>us</Text>
                  </View>
                </View>
              </View>
              <Text style={styles.helperText}>
                T2 must be &lt;= 2 x T1 (physics constraint)
              </Text>
            </>
          )}
        </>
      )}

      {/* Separator */}
      <View style={styles.separator} />

      {/* Readout error + balance circuit (always visible) */}
      <Text style={styles.label}>Readout Error</Text>
      <ConfigSlider
        label="Readout Error Rate"
        value={readoutErrorRate ?? 0}
        min={0}
        max={0.5}
        step={0.01}
        onValueChange={(v) => setReadoutErrorRate(v)}
        formatValue={(v) => v.toFixed(2)}
      />

      <View style={styles.toggleRow}>
        <View style={styles.toggleLabel}>
          <Text style={styles.label}>Balance Circuit</Text>
          <Text style={styles.helperText}>
            Pads with identity gates to equalize depth across state types
          </Text>
        </View>
        <Switch
          value={balanceCircuit}
          onValueChange={setBalanceCircuit}
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
  infoBanner: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(99, 102, 241, 0.08)",
    borderLeftWidth: 4,
    borderLeftColor: colors.status.info,
    borderRadius: radii.sm,
    paddingHorizontal: 10,
    paddingVertical: 8,
    marginBottom: spacing.md,
  },
  infoBannerIcon: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 1,
    borderColor: colors.status.info,
    alignItems: "center",
    justifyContent: "center",
    marginRight: spacing.sm,
  },
  infoBannerIconText: {
    fontSize: 10,
    fontWeight: "700",
    color: colors.status.info,
  },
  infoBannerText: {
    fontSize: 12,
    color: colors.text.primary,
    flex: 1,
  },
  thermalRow: {
    flexDirection: "row",
    gap: spacing.md,
    marginBottom: spacing.xs,
  },
  thermalField: {
    flex: 1,
  },
  inputWithUnit: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  textInput: {
    flex: 1,
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 8,
    padding: 10,
    color: "#e2e8f0",
    fontSize: 13,
  },
  unitLabel: {
    fontSize: 13,
    color: colors.text.secondary,
  },
  helperText: {
    fontSize: 11,
    color: colors.text.tertiary,
    marginBottom: spacing.md,
  },
  separator: {
    height: 1,
    backgroundColor: "#334155",
    marginVertical: spacing.md,
  },
  toggleRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.md,
  },
  toggleLabel: {
    flex: 1,
    marginRight: spacing.md,
  },
});
