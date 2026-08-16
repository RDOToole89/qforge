import type { ReactElement } from "react";
import { Text as RNText, type TextProps as RNTextProps } from "react-native";

import { cn } from "../tv";
import { text, type TextVariants } from "./Text.styles";

export interface TextProps extends RNTextProps, TextVariants {
  className?: string;
}

/**
 * Typographic primitive. Wraps RN `Text`, mapping `variant`/`tone`/`weight`/
 * `mono` onto the design system's semantic type scale.
 */
export function Text({
  variant,
  tone,
  weight,
  mono,
  className,
  ...rest
}: TextProps): ReactElement {
  return (
    <RNText
      className={cn(text({ variant, tone, weight, mono }), className)}
      {...rest}
    />
  );
}

/** Section heading — `variant="heading"`, semibold. */
export function Heading(props: TextProps): ReactElement {
  return <Text variant="heading" weight="semibold" {...props} />;
}

/** Small de-emphasized caption — `variant="caption"`, tertiary tone. */
export function Caption(props: TextProps): ReactElement {
  return <Text variant="caption" tone="tertiary" {...props} />;
}

/** Form / control label — `variant="label"`, medium weight. */
export function Label(props: TextProps): ReactElement {
  return <Text variant="label" weight="medium" {...props} />;
}
