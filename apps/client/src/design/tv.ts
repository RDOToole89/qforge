/**
 * Configured `tailwind-variants` entry point.
 *
 * All design-system primitives must import `tv` (and `cn`/`cx`) from HERE — not
 * from `tailwind-variants` directly — so they share one `tailwind-merge`
 * configuration.
 *
 * Why the custom config: our semantic type scale registers font-size utilities
 * named after the token keys (`text-body`, `text-label`, `text-heading`, …).
 * tailwind-merge does not know these are font sizes, so without help it would
 * treat `text-secondary` (a COLOR) and `text-body` (a SIZE) as the same group
 * and drop one when merging. We register the scale's keys under the `font-size`
 * merge group so color + size classes coexist correctly.
 */
import { createTV } from "tailwind-variants";

import { fontSize } from "./tokens";

// The semantic type-scale keys — kept in lockstep with the token source.
const FONT_SIZE_KEYS = Object.keys(fontSize);

export const tv = createTV({
  twMergeConfig: {
    extend: {
      classGroups: {
        "font-size": [{ text: FONT_SIZE_KEYS }],
      },
    },
  },
});

export { cn, cx } from "tailwind-variants";
export type { VariantProps } from "tailwind-variants";
