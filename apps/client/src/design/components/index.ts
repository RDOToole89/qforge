/**
 * Design-system primitive components — public barrel.
 *
 * Exports every primitive plus its `tv` recipe and `VariantProps` types so
 * consumers can compose or extend the variant mappings.
 */

// Text
export { Text, Heading, Caption, Label, type TextProps } from "./Text";
export { text, type TextVariants } from "./Text.styles";

// Button
export { Button, type ButtonProps } from "./Button";
export { button, buttonLabel, type ButtonVariants } from "./Button.styles";

// Card
export { Card, type CardProps } from "./Card";
export { card, type CardVariants } from "./Card.styles";

// Stack
export { Stack, type StackProps } from "./Stack";
export {
  stack,
  layoutVariants,
  layoutDefaults,
  type StackVariants,
} from "./Stack.styles";

// Row
export { Row, type RowProps } from "./Row";
export { row, type RowVariants } from "./Row.styles";

// Chip
export { Chip, type ChipProps } from "./Chip";
export { chip, chipLabel, type ChipVariants } from "./Chip.styles";

// Badge
export { Badge, type BadgeProps } from "./Badge";
export { badge, badgeLabel, type BadgeVariants } from "./Badge.styles";

// SegmentedControl
export {
  SegmentedControl,
  type SegmentedControlProps,
  type SegmentOption,
} from "./SegmentedControl";
export {
  segmentedControl,
  segment,
  segmentLabel,
  type SegmentVariants,
} from "./SegmentedControl.styles";
