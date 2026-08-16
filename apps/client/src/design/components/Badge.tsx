import type { ReactElement } from "react";
import { Text as RNText, View, type ViewProps } from "react-native";

import { cn } from "../tv";
import { badge, badgeLabel, type BadgeVariants } from "./Badge.styles";

export interface BadgeProps extends ViewProps, BadgeVariants {
  label: string;
  className?: string;
}

/** Small static tonal pill primitive (non-interactive). */
export function Badge({
  tone,
  label,
  className,
  ...rest
}: BadgeProps): ReactElement {
  return (
    <View className={cn(badge({ tone }), className)} {...rest}>
      <RNText className={badgeLabel({ tone })}>{label}</RNText>
    </View>
  );
}
