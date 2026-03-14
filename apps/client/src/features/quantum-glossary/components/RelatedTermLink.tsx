import React from "react";
import { TouchableOpacity, Text, StyleSheet } from "react-native";
import { TERM_MAP } from "../data";

interface RelatedTermLinkProps {
  termId: string;
  onPress: (termId: string) => void;
}

export function RelatedTermLink({ termId, onPress }: RelatedTermLinkProps) {
  const term = TERM_MAP[termId];
  const label = term?.name ?? termId;

  return (
    <TouchableOpacity style={styles.chip} onPress={() => onPress(termId)}>
      <Text style={styles.text}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  chip: {
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 5,
    marginRight: 6,
    marginBottom: 6,
  },
  text: {
    color: "#818cf8",
    fontSize: 13,
  },
});
