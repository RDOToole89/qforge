import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  LayoutAnimation,
} from "react-native";
import FontAwesome from "@expo/vector-icons/FontAwesome";
import { MathFormula } from "./MathFormula";

interface FormulaSectionProps {
  latex: string;
  explanation?: string;
}

export function FormulaSection({ latex, explanation }: FormulaSectionProps) {
  const [showExplanation, setShowExplanation] = useState(false);

  const toggleExplanation = () => {
    if (!explanation) return;
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setShowExplanation((v) => !v);
  };

  return (
    <View style={styles.container}>
      <View style={styles.labelRow}>
        <Text style={styles.sectionLabel}>Key Equation</Text>
        {explanation && (
          <TouchableOpacity
            onPress={toggleExplanation}
            style={styles.infoButton}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          >
            <FontAwesome
              name="info-circle"
              size={14}
              color={showExplanation ? "#818cf8" : "#64748b"}
            />
            <Text
              style={[
                styles.infoText,
                showExplanation && styles.infoTextActive,
              ]}
            >
              {showExplanation ? "hide explanation" : "what does this mean?"}
            </Text>
          </TouchableOpacity>
        )}
      </View>

      <TouchableOpacity
        activeOpacity={explanation ? 0.7 : 1}
        onPress={toggleExplanation}
        style={styles.formulaContainer}
      >
        <MathFormula latex={latex} />
      </TouchableOpacity>

      {showExplanation && explanation && (
        <View style={styles.explanationBox}>
          <View style={styles.explanationAccent} />
          <Text style={styles.explanationText}>{explanation}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: 8,
    marginBottom: 4,
  },
  labelRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  sectionLabel: {
    color: "#6366f1",
    fontSize: 12,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  infoButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  infoText: {
    color: "#64748b",
    fontSize: 11,
    fontStyle: "italic",
  },
  infoTextActive: {
    color: "#818cf8",
  },
  formulaContainer: {
    backgroundColor: "#0f172a",
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#1e293b",
    overflow: "hidden",
  },
  explanationBox: {
    flexDirection: "row",
    marginTop: 6,
    backgroundColor: "#1a1f35",
    borderRadius: 6,
    padding: 10,
    paddingLeft: 0,
    overflow: "hidden",
  },
  explanationAccent: {
    width: 3,
    backgroundColor: "#818cf8",
    borderTopLeftRadius: 6,
    borderBottomLeftRadius: 6,
    marginRight: 10,
  },
  explanationText: {
    flex: 1,
    color: "#c7d2fe",
    fontSize: 13,
    lineHeight: 19,
    fontStyle: "italic",
  },
});
