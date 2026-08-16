import type { GlossaryCategory, GlossaryTerm } from "../types";

import * as fundamentals from "./fundamentals";
import * as gates from "./gates";
import * as states from "./states";
import * as blochSphere from "./bloch-sphere";
import * as entanglement from "./entanglement";
import * as densityMatrices from "./density-matrices";
import * as noise from "./noise";
import * as decoherence from "./decoherence";
import * as measurement from "./measurement";
import * as information from "./information";
import * as errorCorrection from "./error-correction";
import * as linearAlgebra from "./linear-algebra";
import * as distributionMetrics from "./distribution-metrics";
import * as hardware from "./hardware";
import * as algorithms from "./algorithms";
import * as openQuantumSystems from "./open-quantum-systems";

const modules = [
  fundamentals,
  gates,
  states,
  blochSphere,
  entanglement,
  densityMatrices,
  noise,
  decoherence,
  measurement,
  information,
  errorCorrection,
  linearAlgebra,
  distributionMetrics,
  openQuantumSystems,
  hardware,
  algorithms,
];

export const categories: GlossaryCategory[] = modules.map((m) => m.category);

export const terms: GlossaryTerm[] = modules.flatMap((m) => m.terms);

export const TERM_MAP: Record<string, GlossaryTerm> = Object.fromEntries(
  terms.map((t) => [t.id, t])
);

export const CATEGORY_MAP: Record<string, GlossaryCategory> = Object.fromEntries(
  categories.map((c) => [c.id, c])
);

export function getTermsByCategory(categoryId: string): GlossaryTerm[] {
  return terms.filter((t) => t.categoryId === categoryId);
}
