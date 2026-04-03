/** A reference link for further study */
export interface FurtherReading {
  title: string;
  url: string;
  /** 'textbook' | 'paper' | 'lecture' | 'interactive' | 'wiki' */
  type: 'textbook' | 'paper' | 'lecture' | 'interactive' | 'wiki';
  /** Brief note on why this resource is useful */
  note?: string;
}

/** A single glossary term */
export interface GlossaryTerm {
  id: string;
  name: string;
  formalDefinition: string;
  intuitiveExplanation: string;
  symbol?: string;
  /** Key equation or formula in LaTeX notation */
  keyEquation?: string;
  /** Plain-English explanation of what the key equation represents */
  formulaExplanation?: string;
  relatedTerms: string[];
  categoryId: string;
  /** Links to academic resources for deeper study */
  furtherReading?: FurtherReading[];
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
