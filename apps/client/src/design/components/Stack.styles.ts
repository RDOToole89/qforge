/**
 * `Stack` recipe — vertical flex layout. Shares its `gap`/`align`/`justify`
 * variant maps with `Row` (re-exported below). Pure class mapping; no
 * rendering. See `Stack.tsx`.
 */
import { tv, type VariantProps } from "../tv";

/** Shared layout variant maps, reused by both `stack` and `row`. */
export const layoutVariants = {
  gap: {
    none: "gap-0",
    xs: "gap-xs",
    sm: "gap-sm",
    md: "gap-md",
    lg: "gap-lg",
    xl: "gap-xl",
    "2xl": "gap-2xl",
  },
  align: {
    start: "items-start",
    center: "items-center",
    end: "items-end",
    stretch: "items-stretch",
  },
  justify: {
    start: "justify-start",
    center: "justify-center",
    end: "justify-end",
    between: "justify-between",
  },
} as const;

export const layoutDefaults = {
  gap: "none",
  align: "stretch",
  justify: "start",
} as const;

export const stack = tv({
  base: "flex flex-col",
  variants: layoutVariants,
  defaultVariants: layoutDefaults,
});

export type StackVariants = VariantProps<typeof stack>;
