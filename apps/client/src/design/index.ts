/**
 * Design system — top-level public entry point.
 *
 * Re-exports the design tokens, the configured `tv`/`cn` helpers, and all
 * primitive components. Feature code should import from here (`@/src/design`).
 */
export * from "./tokens";
export { tv, cn, cx, type VariantProps } from "./tv";
export * from "./components";
