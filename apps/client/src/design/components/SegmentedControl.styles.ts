/**
 * `SegmentedControl` recipes — the container track (`segmentedControl`), each
 * pressable `segment`, and its `segmentLabel`. Pure class mapping; no
 * rendering. See `SegmentedControl.tsx`.
 */
import { tv, type VariantProps } from "../tv";

export const segmentedControl = tv({
  base: "flex-row gap-xs rounded-md bg-surface p-xs",
});

export const segment = tv({
  base: "flex-1 items-center justify-center rounded-sm px-md py-sm",
  variants: {
    selected: {
      true: "bg-accent",
      false: "bg-transparent",
    },
  },
  defaultVariants: {
    selected: false,
  },
});

export const segmentLabel = tv({
  base: "text-label font-medium",
  variants: {
    selected: {
      true: "text-primary",
      false: "text-secondary",
    },
  },
  defaultVariants: {
    selected: false,
  },
});

export type SegmentVariants = VariantProps<typeof segment>;
