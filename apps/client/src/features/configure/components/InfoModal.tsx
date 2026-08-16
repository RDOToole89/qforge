import React from "react";
import { Modal, Pressable, ScrollView } from "react-native";

import { Text } from "@/src/design";
import { INFO_TEXT } from "../constants";

interface InfoModalProps {
  visible: boolean;
  infoKey: string | null;
  onClose: () => void;
}

export function InfoModal({ visible, infoKey, onClose }: InfoModalProps) {
  const entry = infoKey != null ? INFO_TEXT[infoKey] : null;

  if (entry == null) {
    return null;
  }

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <Pressable
        className="flex-1 items-center justify-center"
        style={{ backgroundColor: "rgba(0, 0, 0, 0.6)" }}
        onPress={onClose}
      >
        <Pressable
          className="rounded-xl border border-default bg-surface p-2xl"
          style={{ maxWidth: 500, maxHeight: "80%", width: "90%" }}
          onPress={() => {}}
        >
          <ScrollView showsVerticalScrollIndicator={false}>
            <Text variant="heading" weight="bold" className="mb-lg">
              {entry.title}
            </Text>
            <Text variant="label" weight="regular" tone="secondary" style={{ lineHeight: 22 }}>
              {entry.content}
            </Text>
          </ScrollView>

          <Pressable onPress={onClose} className="mt-lg items-center py-md">
            <Text weight="semibold" tone="accent" style={{ fontSize: 15 }}>
              Got it
            </Text>
          </Pressable>
        </Pressable>
      </Pressable>
    </Modal>
  );
}
