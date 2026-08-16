import React from "react";
import { TextInput, TouchableOpacity } from "react-native";
import FontAwesome from "@expo/vector-icons/FontAwesome";

import { Row, chrome } from "@/src/design";

interface SearchBarProps {
  value: string;
  onChangeText: (text: string) => void;
}

export function SearchBar({ value, onChangeText }: SearchBarProps) {
  return (
    <Row className="mx-lg my-sm h-10 rounded-lg border border-default bg-surface px-md">
      <FontAwesome
        name="search"
        size={14}
        color={chrome.text.tertiary}
        style={{ marginRight: 8 }}
      />
      <TextInput
        className="flex-1 text-label text-primary"
        placeholder="Search terms, definitions..."
        placeholderTextColor={chrome.text.tertiary}
        value={value}
        onChangeText={onChangeText}
        autoCapitalize="none"
        autoCorrect={false}
        clearButtonMode="while-editing"
      />
      {value.length > 0 && (
        <TouchableOpacity onPress={() => onChangeText("")} className="p-xs">
          <FontAwesome
            name="times-circle"
            size={16}
            color={chrome.text.tertiary}
          />
        </TouchableOpacity>
      )}
    </Row>
  );
}
