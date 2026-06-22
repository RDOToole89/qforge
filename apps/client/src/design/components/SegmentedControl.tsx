import type { ReactElement } from "react";
import { Pressable, Text as RNText, View } from "react-native";

import { cn } from "../tv";
import {
  segment,
  segmentedControl,
  segmentLabel,
} from "./SegmentedControl.styles";

export interface SegmentOption<T extends string = string> {
  label: string;
  value: T;
}

export interface SegmentedControlProps<T extends string = string> {
  options: SegmentOption<T>[];
  value: T;
  onChange: (value: T) => void;
  className?: string;
}

/** Controlled segmented control. Selected segment uses `bg-accent`. */
export function SegmentedControl<T extends string = string>({
  options,
  value,
  onChange,
  className,
}: SegmentedControlProps<T>): ReactElement {
  return (
    <View className={cn(segmentedControl(), className)}>
      {options.map((option) => {
        const selected = option.value === value;
        return (
          <Pressable
            key={option.value}
            accessibilityRole="button"
            accessibilityState={{ selected }}
            onPress={() => onChange(option.value)}
            className={segment({ selected })}
          >
            <RNText className={segmentLabel({ selected })}>
              {option.label}
            </RNText>
          </Pressable>
        );
      })}
    </View>
  );
}
