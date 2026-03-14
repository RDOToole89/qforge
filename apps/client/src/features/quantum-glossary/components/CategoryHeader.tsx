import React from "react";
import { View, Text, StyleSheet } from "react-native";
import FontAwesome from "@expo/vector-icons/FontAwesome";
import type { GlossaryCategory } from "../types";

interface CategoryHeaderProps {
  category: GlossaryCategory;
  termCount: number;
}

const ICON_MAP: Record<string, React.ComponentProps<typeof FontAwesome>["name"]> = {
  atom: "circle-o",
  microchip: "microchip",
  link: "link",
  "chart-pie": "pie-chart",
  "wave-square": "signal",
  table: "table",
  shield: "shield",
  calculator: "calculator",
  crosshairs: "crosshairs",
  water: "tint",
  "info-circle": "info-circle",
  "git-branch": "code-fork",
  cpu: "microchip",
  code: "code",
  globe: "globe",
};

export function CategoryHeader({ category, termCount }: CategoryHeaderProps) {
  const iconName = ICON_MAP[category.icon] ?? "circle";

  return (
    <View style={[styles.container, { borderLeftColor: category.color }]}>
      <FontAwesome
        name={iconName}
        size={16}
        color={category.color}
        style={styles.icon}
      />
      <View style={styles.text}>
        <Text style={styles.name}>{category.name}</Text>
        <Text style={styles.description}>
          {category.description} · {termCount} terms
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#0f172a",
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderLeftWidth: 3,
    marginTop: 8,
  },
  icon: {
    marginRight: 10,
    width: 20,
    textAlign: "center",
  },
  text: {
    flex: 1,
  },
  name: {
    color: "#f1f5f9",
    fontSize: 15,
    fontWeight: "700",
  },
  description: {
    color: "#64748b",
    fontSize: 12,
    marginTop: 2,
  },
});
