import type { ReactElement } from "react";
import { Pressable, type PressableProps, Text as RNText } from "react-native";

import { cn } from "../tv";
import { chip, chipLabel, type ChipVariants } from "./Chip.styles";

export interface ChipProps
  extends Omit<PressableProps, "children">,
    ChipVariants {
  label: string;
  className?: string;
}

/** Selectable tonal pill primitive. */
export function Chip({
  tone,
  selected,
  label,
  className,
  ...rest
}: ChipProps): ReactElement {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ selected: Boolean(selected) }}
      className={cn(chip({ tone, selected }), className)}
      {...rest}
    >
      <RNText className={chipLabel({ tone })}>{label}</RNText>
    </Pressable>
  );
}
