import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

interface Props {
  name: string;
  description: string;
  onRun: () => void;
  onCustomize: () => void;
}

export default function ExperimentCard({
  name,
  description,
  onRun,
  onCustomize,
}: Props) {
  return (
    <View style={styles.card}>
      <Text style={styles.name}>{name}</Text>
      <Text style={styles.description}>{description}</Text>
      <View style={styles.actions}>
        <Pressable
          style={({ pressed }) => [styles.btn, styles.runBtn, pressed && styles.pressed]}
          onPress={onRun}
        >
          <Text style={styles.btnText}>Run</Text>
        </Pressable>
        <Pressable
          style={({ pressed }) => [styles.btn, styles.customizeBtn, pressed && styles.pressed]}
          onPress={onCustomize}
        >
          <Text style={[styles.btnText, { color: "#a5b4fc" }]}>Customize</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#334155",
  },
  name: {
    color: "#e2e8f0",
    fontSize: 16,
    fontWeight: "700",
    fontFamily: "SpaceMono",
    marginBottom: 4,
  },
  description: { color: "#94a3b8", fontSize: 13, marginBottom: 12 },
  actions: { flexDirection: "row", gap: 8 },
  btn: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: "center",
  },
  runBtn: { backgroundColor: "#6366f1" },
  customizeBtn: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: "#6366f1",
  },
  btnText: { color: "#fff", fontSize: 14, fontWeight: "600" },
  pressed: { opacity: 0.7 },
});
