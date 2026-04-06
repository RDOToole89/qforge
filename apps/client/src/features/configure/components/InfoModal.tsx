import React from "react";
import {
  Modal,
  View,
  Text,
  Pressable,
  StyleSheet,
  ScrollView,
} from "react-native";
import { colors, spacing, radii } from "@/src/theme";
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
      <Pressable style={styles.overlay} onPress={onClose}>
        <Pressable style={styles.card} onPress={() => {}}>
          <ScrollView showsVerticalScrollIndicator={false}>
            <Text style={styles.title}>{entry.title}</Text>
            <Text style={styles.content}>{entry.content}</Text>
          </ScrollView>

          <Pressable onPress={onClose} style={styles.closeButton}>
            <Text style={styles.closeText}>Got it</Text>
          </Pressable>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    justifyContent: "center",
    alignItems: "center",
  },
  card: {
    backgroundColor: colors.bg.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.lg,
    padding: spacing.xl,
    maxWidth: 500,
    maxHeight: "80%",
    width: "90%",
  },
  title: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.text.primary,
    marginBottom: spacing.lg,
  },
  content: {
    fontSize: 14,
    lineHeight: 22,
    color: colors.text.secondary,
  },
  closeButton: {
    alignItems: "center",
    paddingVertical: spacing.md,
    marginTop: spacing.lg,
  },
  closeText: {
    fontSize: 15,
    fontWeight: "600",
    color: colors.accent.base,
  },
});
