/**
 * `Row` recipe — horizontal flex layout. Reuses the shared `gap`/`align`/
 * `justify` maps from `Stack.styles`. Pure class mapping; no rendering. See
 * `Row.tsx`.
 */
import { tv, type VariantProps } from "../tv";
import { layoutDefaults, layoutVariants } from "./Stack.styles";

export const row = tv({
  base: "flex flex-row",
  variants: layoutVariants,
  defaultVariants: { ...layoutDefaults, align: "center" },
});

export type RowVariants = VariantProps<typeof row>;
