/** A single glossary term */
export interface GlossaryTerm {
  id: string;
  name: string;
  formalDefinition: string;
  intuitiveExplanation: string;
  symbol?: string;
  relatedTerms: string[];
  categoryId: string;
}

/** A topic category grouping related terms */
export interface GlossaryCategory {
  id: string;
  name: string;
  icon: string;
  color: string;
  description: string;
}

/** Complete glossary dataset */
export interface GlossaryData {
  categories: GlossaryCategory[];
  terms: GlossaryTerm[];
}
