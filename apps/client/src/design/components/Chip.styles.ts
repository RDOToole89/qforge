/**
 * `Chip` recipes — pill container (`chip`) + its label (`chipLabel`). A chip is
 * a selectable, tonal pill. Pure class mapping; no rendering. See `Chip.tsx`.
 */
import { tv, type VariantProps } from "../tv";

export const chip = tv({
  base: "flex-row items-center self-start rounded-pill border border-transparent px-md py-xs",
  variants: {
    tone: {
      neutral: "bg-elevated",
      accent: "bg-accent",
      success: "bg-success",
      warning: "bg-warning",
      error: "bg-error",
      info: "bg-info",
    },
    selected: {
      true: "border-accent-light",
      false: "",
    },
  },
  defaultVariants: {
    tone: "neutral",
    selected: false,
  },
});

export const chipLabel = tv({
  base: "text-bodySm font-medium",
  variants: {
    tone: {
      neutral: "text-secondary",
      accent: "text-primary",
      success: "text-primary",
      warning: "text-primary",
      error: "text-primary",
      info: "text-primary",
    },
  },
  defaultVariants: {
    tone: "neutral",
  },
});

export type ChipVariants = VariantProps<typeof chip>;
