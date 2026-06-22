/**
 * `Button` recipes — the Pressable container (`button`) and its text label
 * (`buttonLabel`). Pure class mapping; no rendering. See `Button.tsx`.
 */
import { tv, type VariantProps } from "../tv";

export const button = tv({
  base: "flex-row items-center justify-center rounded-md",
  variants: {
    variant: {
      primary: "bg-accent",
      secondary: "bg-elevated",
      outline: "border border-default bg-transparent",
      ghost: "bg-transparent",
      danger: "bg-error",
    },
    size: {
      sm: "gap-xs px-md py-xs",
      md: "gap-sm px-lg py-sm",
      lg: "gap-sm px-xl py-md",
    },
    fullWidth: {
      true: "w-full",
      false: "self-start",
    },
    disabled: {
      true: "opacity-50",
      false: "",
    },
  },
  defaultVariants: {
    variant: "primary",
    size: "md",
    fullWidth: false,
    disabled: false,
  },
});

export const buttonLabel = tv({
  base: "font-semibold",
  variants: {
    variant: {
      primary: "text-primary",
      secondary: "text-primary",
      outline: "text-primary",
      ghost: "text-secondary",
      danger: "text-primary",
    },
    size: {
      sm: "text-bodySm",
      md: "text-label",
      lg: "text-headingSm",
    },
  },
  defaultVariants: {
    variant: "primary",
    size: "md",
  },
});

export type ButtonVariants = VariantProps<typeof button>;
