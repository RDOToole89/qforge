/**
 * `Card` recipe — surface container with elevation/border variants and padding
 * scale. Pure class mapping; no rendering. See `Card.tsx`.
 */
import { tv, type VariantProps } from "../tv";

export const card = tv({
  base: "rounded-lg bg-surface",
  variants: {
    variant: {
      elevated: "border border-subtle shadow-level1",
      flat: "",
      outlined: "border border-default",
    },
    padding: {
      none: "",
      sm: "p-sm",
      md: "p-md",
      lg: "p-lg",
    },
  },
  defaultVariants: {
    variant: "elevated",
    padding: "md",
  },
});

export type CardVariants = VariantProps<typeof card>;
