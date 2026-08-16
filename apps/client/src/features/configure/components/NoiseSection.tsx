import React from "react";
import { StyleSheet, TextInput, Switch, View } from "react-native";

import { Chip, Row, Text, chrome } from "@/src/design";
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
    <View className="mb-lg">
      <SectionHeader
        title="Noise"
        switchValue={noiseEnabled}
        onSwitchChange={setNoiseEnabled}
        onInfo={onInfo}
        disabled={noiseDisabledReason !== null}
      />

      {/* Disabled reason banner */}
      {noiseDisabledReason !== null && (
        <Row align="center" className="mb-md rounded-md" style={styles.infoBanner}>
          <View className="mr-sm items-center justify-center rounded-pill border border-info" style={styles.infoBannerIcon}>
            <Text variant="caption" weight="bold" tone="accent">i</Text>
          </View>
          <Text variant="body" className="flex-1">{noiseDisabledReason}</Text>
        </Row>
      )}

      {/* Noise type + error rate (only when enabled) */}
      {noiseEnabled && (
        <>
          <Text variant="label" weight="semibold" className="mb-xs">Noise Type</Text>
          <View className="mb-md flex-row flex-wrap" style={{ gap: 6 }}>
            {NOISE_TYPES.map((nt) => {
              const active = noiseType === nt.id;
              return (
                <Chip
                  key={nt.id}
                  label={nt.label}
                  tone={active ? "accent" : "neutral"}
                  selected={active}
                  onPress={() => setNoiseType(nt.id as NoiseType)}
                />
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
              <Row className="mb-xs" style={{ gap: 12 }}>
                <View className="flex-1">
                  <Text variant="label" weight="semibold" className="mb-xs">T1</Text>
                  <Row align="center" style={{ gap: 4 }}>
                    <TextInput
                      style={styles.textInput}
                      keyboardType="numeric"
                      placeholder="100"
                      placeholderTextColor={chrome.text.tertiary}
                      value={t1 !== null ? String(t1) : ""}
                      onChangeText={handleT1Change}
                    />
                    <Text variant="bodyLg" tone="secondary">us</Text>
                  </Row>
                </View>
                <View className="flex-1">
                  <Text variant="label" weight="semibold" className="mb-xs">T2</Text>
                  <Row align="center" style={{ gap: 4 }}>
                    <TextInput
                      style={styles.textInput}
                      keyboardType="numeric"
                      placeholder="80"
                      placeholderTextColor={chrome.text.tertiary}
                      value={t2 !== null ? String(t2) : ""}
                      onChangeText={handleT2Change}
                    />
                    <Text variant="bodyLg" tone="secondary">us</Text>
                  </Row>
                </View>
              </Row>
              <Text variant="bodySm" tone="tertiary" className="mb-md">
                T2 must be &lt;= 2 x T1 (physics constraint)
              </Text>
            </>
          )}
        </>
      )}

      {/* Separator */}
      <View className="my-md h-px bg-default" />

      {/* Readout error + balance circuit (always visible) */}
      <Text variant="label" weight="semibold" className="mb-xs">Readout Error</Text>
      <ConfigSlider
        label="Readout Error Rate"
        value={readoutErrorRate ?? 0}
        min={0}
        max={0.5}
        step={0.01}
        onValueChange={(v) => setReadoutErrorRate(v)}
        formatValue={(v) => v.toFixed(2)}
      />

      <Row align="center" justify="between" className="mb-md">
        <View className="mr-md flex-1">
          <Text variant="label" weight="semibold" className="mb-xs">Balance Circuit</Text>
          <Text variant="bodySm" tone="tertiary">
            Pads with identity gates to equalize depth across state types
          </Text>
        </View>
        <Switch
          value={balanceCircuit}
          onValueChange={setBalanceCircuit}
          trackColor={{ false: chrome.text.tertiary, true: chrome.accent.base }}
          thumbColor={chrome.text.primary}
        />
      </Row>
    </View>
  );
}

const styles = StyleSheet.create({
  textInput: {
    flex: 1,
    backgroundColor: chrome.bg.surface,
    borderWidth: 1,
    borderColor: chrome.border.default,
    borderRadius: 8,
    padding: 10,
    color: chrome.text.primary,
    fontSize: 13,
  },
  infoBanner: {
    backgroundColor: "rgba(99, 102, 241, 0.08)",
    borderLeftWidth: 4,
    borderLeftColor: chrome.status.info,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  infoBannerIcon: {
    width: 18,
    height: 18,
  },
});
