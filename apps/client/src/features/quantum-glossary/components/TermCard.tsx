import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  LayoutAnimation,
  Platform,
  UIManager,
} from "react-native";
import FontAwesome from "@expo/vector-icons/FontAwesome";
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
      style={[styles.card, highlighted && styles.highlighted]}
    >
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Text style={styles.name}>{term.name}</Text>
          {term.symbol && <SymbolBadge symbol={term.symbol} />}
        </View>
        <FontAwesome
          name={expanded ? "chevron-up" : "chevron-down"}
          size={12}
          color="#64748b"
        />
      </View>

      <Text style={styles.intuitive} numberOfLines={expanded ? undefined : 2}>
        {term.intuitiveExplanation}
      </Text>

      {expanded && (
        <View style={styles.details}>
          <Text style={styles.sectionLabel}>Formal Definition</Text>
          <Text style={styles.formal}>{term.formalDefinition}</Text>

          {term.keyEquation && (
            <FormulaSection
              latex={term.keyEquation}
              explanation={term.formulaExplanation}
            />
          )}

          {term.relatedTerms.length > 0 && (
            <>
              <Text style={styles.sectionLabel}>Related</Text>
              <View style={styles.related}>
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
    backgroundColor: "#1e293b",
    borderRadius: 10,
    padding: 14,
    marginHorizontal: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#334155",
  },
  highlighted: {
    borderColor: "#6366f1",
    borderWidth: 2,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  titleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    flex: 1,
  },
  name: {
    color: "#f1f5f9",
    fontSize: 16,
    fontWeight: "600",
  },
  intuitive: {
    color: "#94a3b8",
    fontSize: 14,
    lineHeight: 20,
  },
  details: {
    marginTop: 12,
    borderTopWidth: 1,
    borderTopColor: "#334155",
    paddingTop: 12,
  },
  sectionLabel: {
    color: "#6366f1",
    fontSize: 12,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: 6,
    marginTop: 4,
  },
  formal: {
    color: "#cbd5e1",
    fontSize: 13,
    lineHeight: 19,
    marginBottom: 10,
  },
  related: {
    flexDirection: "row",
    flexWrap: "wrap",
  },
});
