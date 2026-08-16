/**
 * `Text` recipe — maps the semantic type scale, tone, and weight onto Tailwind
 * utility classes. Pure class mapping; no rendering. See `Text.tsx`.
 */
import { tv, type VariantProps } from "../tv";

export const text = tv({
  base: "",
  variants: {
    variant: {
      display: "text-display",
      heading: "text-heading",
      headingSm: "text-headingSm",
      bodyLg: "text-bodyLg",
      body: "text-body",
      bodySm: "text-bodySm",
      label: "text-label",
      caption: "text-caption",
      captionXs: "text-captionXs",
    },
    tone: {
      primary: "text-primary",
      secondary: "text-secondary",
      tertiary: "text-tertiary",
      accent: "text-accent",
      error: "text-error",
      warning: "text-warning",
      success: "text-success",
    },
    weight: {
      regular: "font-normal",
      medium: "font-medium",
      semibold: "font-semibold",
      bold: "font-bold",
    },
    mono: {
      true: "font-mono",
      false: "font-sans",
    },
  },
  defaultVariants: {
    variant: "body",
    tone: "primary",
    weight: "regular",
    mono: false,
  },
});

export type TextVariants = VariantProps<typeof text>;
