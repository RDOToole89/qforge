import React from "react";

import { Chip } from "@/src/design";
import { TERM_MAP } from "../data";

interface RelatedTermLinkProps {
  termId: string;
  onPress: (termId: string) => void;
}

export function RelatedTermLink({ termId, onPress }: RelatedTermLinkProps) {
  const term = TERM_MAP[termId];
  const label = term?.name ?? termId;

  return (
    <Chip
      label={label}
      onPress={() => onPress(termId)}
      className="mr-xs mb-xs"
    />
  );
}
