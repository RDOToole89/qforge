import React from "react";
import { StyleSheet, Text, View } from "react-native";
import Slider from "@react-native-community/slider";

interface Props {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onValueChange: (v: number) => void;
  formatValue?: (v: number) => string;
}

export default function ConfigSlider({
  label,
  value,
  min,
  max,
  step,
  onValueChange,
  formatValue,
}: Props) {
  const display = formatValue ? formatValue(value) : String(value);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.label}>{label}</Text>
        <Text style={styles.value}>{display}</Text>
      </View>
      <Slider
        style={styles.slider}
        minimumValue={min}
        maximumValue={max}
        step={step}
        value={value}
        onValueChange={onValueChange}
        minimumTrackTintColor="#6366f1"
        maximumTrackTintColor="#334155"
        thumbTintColor="#6366f1"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginBottom: 16 },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  label: { color: "#e2e8f0", fontSize: 14, fontWeight: "600" },
  value: { color: "#94a3b8", fontSize: 14, fontFamily: "SpaceMono" },
  slider: { width: "100%", height: 40 },
});
