import React from "react";
import { Pressable, Switch, View } from "react-native";

import { Row, Text, chrome, cn } from "@/src/design";

interface SectionHeaderProps {
  title: string;
  onInfo?: () => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  switchValue?: boolean;
  onSwitchChange?: (v: boolean) => void;
  disabled?: boolean;
}

export function SectionHeader({
  title,
  onInfo,
  collapsed,
  onToggleCollapse,
  switchValue,
  onSwitchChange,
  disabled = false,
}: SectionHeaderProps) {
  return (
    <Row align="center" className={cn("mb-md", disabled && "opacity-50")}>
      <Text
        variant="headingSm"
        weight="bold"
        tone={disabled ? "tertiary" : "primary"}
      >
        {title}
      </Text>

      {onInfo != null && (
        <Pressable
          onPress={onInfo}
          className="ml-sm items-center justify-center rounded-pill border border-tertiary"
          style={{ width: 20, height: 20 }}
          hitSlop={8}
          disabled={disabled}
        >
          <Text variant="bodySm" weight="semibold" tone="secondary">
            i
          </Text>
        </Pressable>
      )}

      <View className="flex-1" />

      {switchValue != null && onSwitchChange != null && (
        <Switch
          value={switchValue}
          onValueChange={onSwitchChange}
          disabled={disabled}
          trackColor={{
            false: chrome.text.tertiary,
            true: chrome.accent.base,
          }}
          thumbColor={chrome.text.primary}
        />
      )}

      {collapsed != null && onToggleCollapse != null && (
        <Pressable onPress={onToggleCollapse} hitSlop={8} disabled={disabled}>
          <Text
            variant="headingSm"
            weight="regular"
            tone={disabled ? "tertiary" : "secondary"}
            className="ml-sm"
          >
            {collapsed ? "▸" : "▾"}
          </Text>
        </Pressable>
      )}
    </Row>
  );
}
