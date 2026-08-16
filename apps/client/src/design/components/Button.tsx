import type { ReactElement, ReactNode } from "react";
import {
  ActivityIndicator,
  Pressable,
  type PressableProps,
  Text as RNText,
} from "react-native";

import { chrome } from "../tokens";
import { cn } from "../tv";
import { button, buttonLabel, type ButtonVariants } from "./Button.styles";

export interface ButtonProps
  extends Omit<PressableProps, "children" | "disabled">,
    ButtonVariants {
  children?: ReactNode;
  iconLeft?: ReactNode;
  iconRight?: ReactNode;
  loading?: boolean;
  className?: string;
}

/**
 * Pressable button primitive. Renders a {@link ActivityIndicator} Spinner while
 * `loading`, and string children inside the design-system label recipe.
 */
export function Button({
  variant,
  size,
  fullWidth,
  disabled,
  loading,
  iconLeft,
  iconRight,
  children,
  className,
  ...rest
}: ButtonProps): ReactElement {
  const isDisabled = Boolean(disabled) || Boolean(loading);

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled: isDisabled, busy: Boolean(loading) }}
      disabled={isDisabled}
      className={cn(
        button({ variant, size, fullWidth, disabled: isDisabled }),
        className,
      )}
      {...rest}
    >
      {loading ? (
        <ActivityIndicator size="small" color={chrome.text.primary} />
      ) : (
        <>
          {iconLeft}
          {typeof children === "string" ? (
            <RNText className={buttonLabel({ variant, size })}>{children}</RNText>
          ) : (
            children
          )}
          {iconRight}
        </>
      )}
    </Pressable>
  );
}
