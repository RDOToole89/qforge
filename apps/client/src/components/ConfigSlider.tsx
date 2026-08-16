import React from "react";
import { StyleSheet, View } from "react-native";
import Slider from "@react-native-community/slider";

import { Row, Text, chrome } from "@/src/design";

interface Props {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onValueChange: (v: number) => void;
  formatValue?: (v: number) => string;
  disabled?: boolean;
}

export default function ConfigSlider({
  label,
  value,
  min,
  max,
  step,
  onValueChange,
  formatValue,
  disabled = false,
}: Props) {
  const display = formatValue ? formatValue(value) : String(value);

  return (
    <View style={[styles.container, disabled && styles.disabled]}>
      <Row justify="between" className="mb-xs">
        <Text variant="label" weight="semibold" tone="primary">
          {label}
        </Text>
        <Text variant="label" tone="secondary" mono>
          {display}
        </Text>
      </Row>
      <Slider
        style={styles.slider}
        minimumValue={min}
        maximumValue={max}
        step={step}
        value={value}
        onValueChange={onValueChange}
        minimumTrackTintColor={chrome.accent.base}
        maximumTrackTintColor={chrome.border.default}
        thumbTintColor={chrome.accent.base}
        disabled={disabled}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginBottom: 16 },
  disabled: { opacity: 0.4 },
  slider: { width: "100%", height: 40 },
});
