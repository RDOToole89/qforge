import React, { useState } from "react";
import {
  View,
  StyleSheet,
  TouchableOpacity,
  LayoutAnimation,
  Platform,
  UIManager,
} from "react-native";
import FontAwesome from "@expo/vector-icons/FontAwesome";

import { Text, card, chrome } from "@/src/design";
import { SymbolBadge } from "./SymbolBadge";
import { RelatedTermLink } from "./RelatedTermLink";
import { FormulaSection } from "./FormulaSection";
import type { GlossaryTerm } from "../types";

if (
  Platform.OS === "android" &&
  UIManager.setLayoutAnimationEnabledExperimental
) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

interface TermCardProps {
  term: GlossaryTerm;
  highlighted?: boolean;
  onRelatedPress: (termId: string) => void;
}

/** Accent, uppercase sub-section label used inside an expanded term card. */
function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <Text
      variant="body"
      weight="bold"
      tone="accent"
      className="mt-xs mb-xs uppercase"
      style={styles.sectionLabel}
    >
      {children}
    </Text>
  );
}

export function TermCard({ term, highlighted, onRelatedPress }: TermCardProps) {
  const [expanded, setExpanded] = useState(false);

  const toggle = () => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpanded((v) => !v);
  };

  return (
    <TouchableOpacity
      activeOpacity={0.8}
      onPress={toggle}
      className={card({
        variant: "outlined",
        padding: "md",
      })}
      style={[styles.card, highlighted && styles.highlighted]}
    >
      <View className="mb-xs flex-row items-center justify-between">
        <View className="flex-1 flex-row items-center gap-sm">
          <Text variant="headingSm" weight="semibold" tone="primary">
            {term.name}
          </Text>
          {term.symbol && <SymbolBadge symbol={term.symbol} />}
        </View>
        <FontAwesome
          name={expanded ? "chevron-up" : "chevron-down"}
          size={12}
          color={chrome.text.tertiary}
        />
      </View>

      <Text
        variant="label"
        weight="regular"
        tone="secondary"
        numberOfLines={expanded ? undefined : 2}
      >
        {term.intuitiveExplanation}
      </Text>

      {expanded && (
        <View className="mt-md border-t border-default pt-md">
          <SectionLabel>Formal Definition</SectionLabel>
          <Text variant="bodyLg" tone="secondary" className="mb-sm">
            {term.formalDefinition}
          </Text>

          {term.keyEquation && (
            <FormulaSection
              latex={term.keyEquation}
              explanation={term.formulaExplanation}
              symbolAnnotations={term.symbolAnnotations}
              termId={term.id}
            />
          )}

          {term.relatedTerms.length > 0 && (
            <>
              <SectionLabel>Related</SectionLabel>
              <View className="flex-row flex-wrap">
                {term.relatedTerms.map((id) => (
                  <RelatedTermLink
                    key={id}
                    termId={id}
                    onPress={onRelatedPress}
                  />
                ))}
              </View>
            </>
          )}
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: 16,
    marginBottom: 8,
  },
  highlighted: {
    borderColor: chrome.accent.base,
    borderWidth: 2,
  },
  sectionLabel: {
    letterSpacing: 0.5,
  },
});
