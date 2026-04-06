import React from "react";
import { View, TextInput, StyleSheet, TouchableOpacity } from "react-native";
import FontAwesome from "@expo/vector-icons/FontAwesome";

interface SearchBarProps {
  value: string;
  onChangeText: (text: string) => void;
}

export function SearchBar({ value, onChangeText }: SearchBarProps) {
  return (
    <View style={styles.container}>
      <FontAwesome name="search" size={14} color="#64748b" style={styles.icon} />
      <TextInput
        style={styles.input}
        placeholder="Search terms, definitions..."
        placeholderTextColor="#64748b"
        value={value}
        onChangeText={onChangeText}
        autoCapitalize="none"
        autoCorrect={false}
        clearButtonMode="while-editing"
      />
      {value.length > 0 && (
        <TouchableOpacity onPress={() => onChangeText("")} style={styles.clear}>
          <FontAwesome name="times-circle" size={16} color="#64748b" />
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#1e293b",
    borderRadius: 10,
    marginHorizontal: 16,
    marginVertical: 8,
    paddingHorizontal: 12,
    height: 40,
    borderWidth: 1,
    borderColor: "#334155",
  },
  icon: {
    marginRight: 8,
  },
  input: {
    flex: 1,
    color: "#e2e8f0",
    fontSize: 15,
  },
  clear: {
    padding: 4,
  },
});
