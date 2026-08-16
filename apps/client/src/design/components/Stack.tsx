import type { ReactElement } from "react";
import { View, type ViewProps } from "react-native";

import { cn } from "../tv";
import { stack, type StackVariants } from "./Stack.styles";

export interface StackProps extends ViewProps, StackVariants {
  className?: string;
}

/** Vertical flex layout primitive with `gap`/`align`/`justify` controls. */
export function Stack({
  gap,
  align,
  justify,
  className,
  ...rest
}: StackProps): ReactElement {
  return (
    <View
      className={cn(stack({ gap, align, justify }), className)}
      {...rest}
    />
  );
}
