import React from "react";
import { View } from "react-native";
import FontAwesome from "@expo/vector-icons/FontAwesome";

import { Text } from "@/src/design";
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
    <View
      className="mt-sm flex-row items-center bg-base px-lg py-sm"
      style={{ borderLeftWidth: 3, borderLeftColor: category.color }}
    >
      <FontAwesome
        name={iconName}
        size={16}
        color={category.color}
        style={{ marginRight: 10, width: 20, textAlign: "center" }}
      />
      <View className="flex-1">
        <Text variant="label" weight="bold" tone="primary">
          {category.name}
        </Text>
        <Text variant="body" tone="tertiary" className="mt-0.5">
          {category.description} · {termCount} terms
        </Text>
      </View>
    </View>
  );
}
