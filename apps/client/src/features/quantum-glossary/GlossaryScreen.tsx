import React, { useState, useMemo, useCallback, useRef } from "react";
import {
  View,
  SectionList,
  type SectionListData,
} from "react-native";

import { Text } from "@/src/design";
import { SearchBar } from "./components/SearchBar";
import { TermCard } from "./components/TermCard";
import { CategoryHeader } from "./components/CategoryHeader";
import { categories, terms, TERM_MAP, CATEGORY_MAP, getTermsByCategory } from "./data";
import type { GlossaryTerm, GlossaryCategory } from "./types";

interface Section {
  category: GlossaryCategory;
  data: GlossaryTerm[];
}

export default function GlossaryScreen() {
  const [query, setQuery] = useState("");
  const [highlightedId, setHighlightedId] = useState<string | null>(null);
  const listRef = useRef<SectionList<GlossaryTerm, Section>>(null);

  const sections: Section[] = useMemo(() => {
    const q = query.toLowerCase().trim();
    return categories
      .map((cat) => {
        const catTerms = getTermsByCategory(cat.id);
        if (!q) return { category: cat, data: catTerms };
        const filtered = catTerms.filter(
          (t) =>
            t.name.toLowerCase().includes(q) ||
            t.formalDefinition.toLowerCase().includes(q) ||
            t.intuitiveExplanation.toLowerCase().includes(q) ||
            (t.symbol && t.symbol.toLowerCase().includes(q))
        );
        return { category: cat, data: filtered };
      })
      .filter((s) => s.data.length > 0);
  }, [query]);

  const totalResults = useMemo(
    () => sections.reduce((sum, s) => sum + s.data.length, 0),
    [sections]
  );

  const navigateToTerm = useCallback(
    (termId: string) => {
      const term = TERM_MAP[termId];
      if (!term) return;

      // Clear search to show all sections
      setQuery("");
      setHighlightedId(termId);

      // Find section and item indices after state update
      setTimeout(() => {
        const sectionIndex = categories.findIndex(
          (c) => c.id === term.categoryId
        );
        if (sectionIndex === -1) return;

        const catTerms = getTermsByCategory(term.categoryId);
        const itemIndex = catTerms.findIndex((t) => t.id === termId);

        listRef.current?.scrollToLocation({
          sectionIndex,
          itemIndex,
          animated: true,
          viewOffset: 60,
        });

        // Clear highlight after a delay
        setTimeout(() => setHighlightedId(null), 2000);
      }, 100);
    },
    []
  );

  const renderSectionHeader = useCallback(
    ({ section }: { section: SectionListData<GlossaryTerm, Section> }) => (
      <CategoryHeader
        category={(section as Section).category}
        termCount={(section as Section).data.length}
      />
    ),
    []
  );

  const renderItem = useCallback(
    ({ item }: { item: GlossaryTerm }) => (
      <TermCard
        term={item}
        highlighted={item.id === highlightedId}
        onRelatedPress={navigateToTerm}
      />
    ),
    [highlightedId, navigateToTerm]
  );

  const keyExtractor = useCallback((item: GlossaryTerm) => item.id, []);

  return (
    <View className="flex-1 bg-base">
      <SearchBar value={query} onChangeText={setQuery} />
      {query.length > 0 && (
        <Text variant="body" tone="tertiary" className="px-lg pb-xs">
          {totalResults} result{totalResults !== 1 ? "s" : ""}
        </Text>
      )}
      <SectionList
        ref={listRef}
        sections={sections}
        keyExtractor={keyExtractor}
        renderItem={renderItem}
        renderSectionHeader={renderSectionHeader}
        stickySectionHeadersEnabled={false}
        contentContainerStyle={{ paddingBottom: 32 }}
        ListEmptyComponent={
          <View className="items-center pt-[60px]">
            <Text variant="label" tone="tertiary">
              No terms match "{query}"
            </Text>
          </View>
        }
        getItemLayout={(_data, index) => ({
          length: 90,
          offset: 90 * index,
          index,
        })}
      />
    </View>
  );
}
