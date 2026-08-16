import type { ReactElement } from "react";
import { View, type ViewProps } from "react-native";

import { cn } from "../tv";
import { row, type RowVariants } from "./Row.styles";

export interface RowProps extends ViewProps, RowVariants {
  className?: string;
}

/** Horizontal flex layout primitive with `gap`/`align`/`justify` controls. */
export function Row({
  gap,
  align,
  justify,
  className,
  ...rest
}: RowProps): ReactElement {
  return (
    <View className={cn(row({ gap, align, justify }), className)} {...rest} />
  );
}
