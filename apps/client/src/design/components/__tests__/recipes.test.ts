/**
 * Recipe contract tests.
 *
 * These lock the variant -> Tailwind-class mapping for every primitive's `tv`
 * recipe. They are pure (no RN rendering): each recipe is a function that
 * returns a className string, so we assert on substrings for representative
 * variant combinations. This guards against accidental drift in the design
 * system's class output without needing a heavy RN render setup.
 */
import { describe, expect, it } from "vitest";

import { badge, badgeLabel } from "../Badge.styles";
import { button, buttonLabel } from "../Button.styles";
import { card } from "../Card.styles";
import { chip, chipLabel } from "../Chip.styles";
import { row } from "../Row.styles";
import {
  segment,
  segmentedControl,
  segmentLabel,
} from "../SegmentedControl.styles";
import { stack } from "../Stack.styles";
import { text } from "../Text.styles";

describe("Text recipe", () => {
  it("maps variant + tone to font-size + color classes", () => {
    const cls = text({ variant: "heading", tone: "secondary" });
    expect(cls).toContain("text-heading");
    expect(cls).toContain("text-secondary");
  });

  it("keeps font-size and color coexisting (tailwind-merge group)", () => {
    const cls = text({ variant: "body", tone: "accent" });
    expect(cls).toContain("text-body");
    expect(cls).toContain("text-accent");
  });

  it("maps weight and mono", () => {
    expect(text({ weight: "bold" })).toContain("font-bold");
    expect(text({ mono: true })).toContain("font-mono");
    expect(text({ mono: false })).toContain("font-sans");
  });

  it("applies defaults (body / primary / regular / sans)", () => {
    const cls = text({});
    expect(cls).toContain("text-body");
    expect(cls).toContain("text-primary");
    expect(cls).toContain("font-normal");
    expect(cls).toContain("font-sans");
  });
});

describe("Button recipe", () => {
  it("primary md includes bg-accent and md padding", () => {
    const cls = button({ variant: "primary", size: "md" });
    expect(cls).toContain("bg-accent");
    expect(cls).toContain("px-lg");
    expect(cls).toContain("rounded-md");
  });

  it("danger includes bg-error", () => {
    expect(button({ variant: "danger" })).toContain("bg-error");
  });

  it("outline includes border-default and transparent bg", () => {
    const cls = button({ variant: "outline" });
    expect(cls).toContain("border-default");
    expect(cls).toContain("bg-transparent");
  });

  it("ghost has transparent bg", () => {
    expect(button({ variant: "ghost" })).toContain("bg-transparent");
  });

  it("fullWidth adds w-full; disabled adds opacity-50", () => {
    expect(button({ fullWidth: true })).toContain("w-full");
    expect(button({ disabled: true })).toContain("opacity-50");
  });

  it("label maps size + variant to text classes", () => {
    expect(buttonLabel({ size: "sm" })).toContain("text-bodySm");
    expect(buttonLabel({ size: "lg" })).toContain("text-headingSm");
    expect(buttonLabel({ variant: "ghost" })).toContain("text-secondary");
  });
});

describe("Card recipe", () => {
  it("base is rounded surface", () => {
    const cls = card({});
    expect(cls).toContain("rounded-lg");
    expect(cls).toContain("bg-surface");
  });

  it("elevated adds shadow-level1 and subtle border", () => {
    const cls = card({ variant: "elevated" });
    expect(cls).toContain("shadow-level1");
    expect(cls).toContain("border-subtle");
  });

  it("outlined includes border-default", () => {
    expect(card({ variant: "outlined" })).toContain("border-default");
  });

  it("flat has no shadow or border", () => {
    const cls = card({ variant: "flat" });
    expect(cls).not.toContain("shadow-level1");
    expect(cls).not.toContain("border-default");
  });

  it("padding maps to spacing utilities", () => {
    expect(card({ padding: "lg" })).toContain("p-lg");
    expect(card({ padding: "none" })).not.toContain("p-");
  });
});

describe("Stack / Row recipes", () => {
  it("stack is flex-col, row is flex-row", () => {
    expect(stack({})).toContain("flex-col");
    expect(row({})).toContain("flex-row");
  });

  it("gap maps to gap-* utilities", () => {
    expect(stack({ gap: "lg" })).toContain("gap-lg");
    expect(row({ gap: "2xl" })).toContain("gap-2xl");
  });

  it("align and justify map to items-* / justify-*", () => {
    const cls = stack({ align: "center", justify: "between" });
    expect(cls).toContain("items-center");
    expect(cls).toContain("justify-between");
  });

  it("row defaults to items-center", () => {
    expect(row({})).toContain("items-center");
  });
});

describe("Chip recipe", () => {
  it("tone maps to bg color", () => {
    expect(chip({ tone: "accent" })).toContain("bg-accent");
    expect(chip({ tone: "success" })).toContain("bg-success");
  });

  it("selected adds accent-light border; unselected does not", () => {
    expect(chip({ tone: "neutral", selected: true })).toContain(
      "border-accent-light",
    );
    expect(chip({ tone: "neutral", selected: false })).not.toContain(
      "border-accent-light",
    );
  });

  it("is a pill", () => {
    expect(chip({})).toContain("rounded-pill");
  });

  it("label tone maps to text color", () => {
    expect(chipLabel({ tone: "neutral" })).toContain("text-secondary");
    expect(chipLabel({ tone: "accent" })).toContain("text-primary");
  });
});

describe("Badge recipe", () => {
  it("is a pill with tone background", () => {
    const cls = badge({ tone: "info" });
    expect(cls).toContain("rounded-pill");
    expect(cls).toContain("bg-info");
  });

  it("label is uppercase captionXs", () => {
    const cls = badgeLabel({ tone: "neutral" });
    expect(cls).toContain("text-captionXs");
    expect(cls).toContain("uppercase");
  });
});

describe("SegmentedControl recipe", () => {
  it("track is a row surface", () => {
    const cls = segmentedControl();
    expect(cls).toContain("flex-row");
    expect(cls).toContain("bg-surface");
  });

  it("selected segment uses bg-accent; unselected is transparent", () => {
    expect(segment({ selected: true })).toContain("bg-accent");
    expect(segment({ selected: false })).toContain("bg-transparent");
  });

  it("selected label is primary; unselected is secondary", () => {
    expect(segmentLabel({ selected: true })).toContain("text-primary");
    expect(segmentLabel({ selected: false })).toContain("text-secondary");
  });
});
