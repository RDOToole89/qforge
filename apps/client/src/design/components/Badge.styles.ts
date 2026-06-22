/**
 * `Badge` recipes — small static tonal pill (`badge`) + its label
 * (`badgeLabel`). Pure class mapping; no rendering. See `Badge.tsx`.
 */
import { tv, type VariantProps } from "../tv";

export const badge = tv({
  base: "flex-row items-center self-start rounded-pill px-sm py-xs",
  variants: {
    tone: {
      neutral: "bg-elevated",
      accent: "bg-accent",
      success: "bg-success",
      warning: "bg-warning",
      error: "bg-error",
      info: "bg-info",
    },
  },
  defaultVariants: {
    tone: "neutral",
  },
});

export const badgeLabel = tv({
  base: "text-captionXs font-semibold uppercase",
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

export type BadgeVariants = VariantProps<typeof badge>;
