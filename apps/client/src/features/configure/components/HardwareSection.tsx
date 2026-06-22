import React, { useState } from "react";
import {
  ActivityIndicator,
  StyleSheet,
  TextInput,
  Switch,
  View,
} from "react-native";

import { Chip, Row, Text, chrome } from "@/src/design";
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
    <View className="mb-lg">
      <SectionHeader title="Hardware" onInfo={onInfo} />

      {/* Backend selection */}
      <Text variant="label" weight="semibold" className="mb-xs">Backend</Text>

      {backendsLoading && (
        <Row align="center" className="mb-md" style={{ gap: 8 }}>
          <ActivityIndicator size="small" color={chrome.accent.base} />
          <Text variant="bodySm" tone="tertiary">Loading backends…</Text>
        </Row>
      )}

      {!backendsLoading && !backendsAvailable && (
        <View className="mb-md rounded-md border border-warning" style={styles.noticeBox}>
          <Text variant="body" weight="semibold">
            No live backends.{" "}
            {backendsReason ?? "IBM Quantum credentials are not configured."}
          </Text>
          <Text variant="bodySm" tone="tertiary" style={{ marginTop: 4 }}>
            Enter a backend name manually below (offline — not verified against a
            real device).
          </Text>
        </View>
      )}

      {backendsAvailable && (
        <View className="mb-md flex-row flex-wrap" style={{ gap: 6 }}>
          {backendNames.map((name) => {
            const active = backendName === name && !showCustom;
            return (
              <Chip
                key={name}
                label={name}
                tone={active ? "accent" : "neutral"}
                selected={active}
                onPress={() => {
                  setBackendName(name);
                  setShowCustom(false);
                }}
              />
            );
          })}
          <Chip
            label="Custom"
            tone={showCustom ? "accent" : "neutral"}
            selected={showCustom}
            onPress={() => {
              setShowCustom(true);
              if (isKnownBackend) setBackendName("");
            }}
          />
        </View>
      )}

      {(showCustom || !backendsAvailable) && (
        <TextInput
          style={styles.textInput}
          placeholder="Enter backend name"
          placeholderTextColor={chrome.text.tertiary}
          value={isKnownBackend ? "" : backendName}
          onChangeText={setBackendName}
          autoCapitalize="none"
          autoCorrect={false}
        />
      )}

      {/* Optimization level */}
      <Text variant="label" weight="semibold" className="mb-xs">Optimization Level</Text>
      <View className="mb-md flex-row flex-wrap" style={{ gap: 6 }}>
        {OPTIMIZATION_LEVELS.map((opt) => {
          const active = optimizationLevel === opt.level;
          return (
            <Chip
              key={opt.level}
              label={`${opt.level} - ${opt.label}`}
              tone={active ? "accent" : "neutral"}
              selected={active}
              onPress={() => setOptimizationLevel(opt.level)}
            />
          );
        })}
      </View>
      {selectedOptLevel && (
        <Text variant="bodySm" tone="tertiary" className="mb-md">
          {selectedOptLevel.description}
        </Text>
      )}

      {/* Hardware session */}
      <Row align="center" justify="between">
        <View className="mr-md flex-1">
          <Text variant="label" weight="semibold" className="mb-xs">Hardware Session</Text>
          <Text variant="bodySm" tone="tertiary">
            Keep backend reserved across sweep jobs
          </Text>
        </View>
        <Switch
          value={hardwareSession}
          onValueChange={setHardwareSession}
          trackColor={{ false: chrome.text.tertiary, true: chrome.accent.base }}
          thumbColor={chrome.text.primary}
        />
      </Row>
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
  noticeBox: {
    backgroundColor: "rgba(245, 158, 11, 0.10)",
    padding: 10,
  },
});
