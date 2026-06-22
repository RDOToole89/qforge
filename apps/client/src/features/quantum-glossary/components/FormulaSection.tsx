import React, { useState } from "react";
import {
  View,
  StyleSheet,
  TouchableOpacity,
  LayoutAnimation,
} from "react-native";
import FontAwesome from "@expo/vector-icons/FontAwesome";

import { Text, chrome } from "@/src/design";
import { MathFormula } from "./MathFormula";

interface FormulaSectionProps {
  latex: string;
  explanation?: string;
  symbolAnnotations?: Record<string, string>;
  termId?: string;
}

export function FormulaSection({ latex, explanation, symbolAnnotations, termId }: FormulaSectionProps) {
  const [showExplanation, setShowExplanation] = useState(false);

  const toggleExplanation = () => {
    if (!explanation) return;
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setShowExplanation((v) => !v);
  };

  return (
    <View className="mt-sm mb-xs">
      <View className="mb-xs flex-row items-center justify-between">
        <Text
          variant="body"
          weight="bold"
          tone="accent"
          className="uppercase"
          style={styles.sectionLabel}
        >
          Key Equation
        </Text>
        {explanation && (
          <TouchableOpacity
            onPress={toggleExplanation}
            className="flex-row items-center gap-xs"
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          >
            <FontAwesome
              name="info-circle"
              size={14}
              color={showExplanation ? chrome.accent.light : chrome.text.tertiary}
            />
            <Text
              variant="bodySm"
              className={showExplanation ? "italic text-accent-light" : "italic text-tertiary"}
            >
              {showExplanation ? "hide explanation" : "what does this mean?"}
            </Text>
          </TouchableOpacity>
        )}
      </View>

      <TouchableOpacity
        activeOpacity={explanation ? 0.7 : 1}
        onPress={toggleExplanation}
        className="overflow-hidden rounded-md border bg-base"
        style={styles.formulaContainer}
      >
        <MathFormula latex={latex} symbolAnnotations={symbolAnnotations} termId={termId} />
      </TouchableOpacity>

      {showExplanation && explanation && (
        <View className="mt-xs flex-row overflow-hidden rounded-sm bg-surface py-sm pr-sm">
          <View style={styles.explanationAccent} />
          <Text
            variant="bodyLg"
            className="flex-1 italic text-accent-light"
          >
            {explanation}
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  sectionLabel: {
    letterSpacing: 0.5,
  },
  formulaContainer: {
    borderColor: chrome.bg.surface,
  },
  explanationAccent: {
    width: 3,
    backgroundColor: chrome.accent.light,
    borderTopLeftRadius: 6,
    borderBottomLeftRadius: 6,
    marginRight: 10,
  },
});
