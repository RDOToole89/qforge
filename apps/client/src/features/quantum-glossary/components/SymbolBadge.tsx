import React from "react";
import { View, Text, StyleSheet } from "react-native";

interface SymbolBadgeProps {
  symbol: string;
}

export function SymbolBadge({ symbol }: SymbolBadgeProps) {
  return (
    <View style={styles.badge}>
      <Text style={styles.text}>{symbol}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    backgroundColor: "#312e81",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    alignSelf: "flex-start",
  },
  text: {
    color: "#a5b4fc",
    fontSize: 13,
    fontFamily: "SpaceMono",
  },
});
