import type { ReactElement } from "react";
import { View, type ViewProps } from "react-native";

import { cn } from "../tv";
import { card, type CardVariants } from "./Card.styles";

export interface CardProps extends ViewProps, CardVariants {
  className?: string;
}

/** Surface container primitive with `variant` (elevation) and `padding` scale. */
export function Card({
  variant,
  padding,
  className,
  ...rest
}: CardProps): ReactElement {
  return (
    <View className={cn(card({ variant, padding }), className)} {...rest} />
  );
}
