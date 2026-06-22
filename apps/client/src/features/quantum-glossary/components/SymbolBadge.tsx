import React from "react";
import { View } from "react-native";

import { Text } from "@/src/design";

interface SymbolBadgeProps {
  symbol: string;
}

export function SymbolBadge({ symbol }: SymbolBadgeProps) {
  return (
    <View className="self-start rounded-md bg-elevated px-sm py-xs">
      <Text variant="bodyLg" mono className="text-accent-light">
        {symbol}
      </Text>
    </View>
  );
}
