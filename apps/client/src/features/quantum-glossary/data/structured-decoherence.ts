import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "structured_decoherence",
  name: "Structured Decoherence",
  icon: "git-branch",
  color: "#f59e0b",
  description: "Research into decoherence pathways and topology-dependent noise",
};

export const terms: GlossaryTerm[] = [
  {
    id: "structured_decoherence",
    name: "Structured Decoherence",
    formalDefinition:
      "The hypothesis that decoherence in entangled systems follows non-random pathways determined by the entanglement topology. Measurable via deviation from null models (factorized distributions) using metrics like Structure Score and Asymmetry Index.",
    intuitiveExplanation:
      "Decoherence isn't just random fog — it flows like a river along the entanglement bonds. How a quantum state falls apart depends on how it was connected. GHZ states decohere differently from W states because their entanglement topology is different.",
    relatedTerms: ["spring_network_model", "structure_score", "asymmetry_index", "decoherence"],
    categoryId: "structured_decoherence",
  },
  {
    id: "spring_network_model",
    name: "Spring Network Model",
    formalDefinition:
      "A physical model where entanglement bonds act as springs under tension. Decoherence flows along the tension patterns of the network. Predicts that error propagation follows the entanglement graph structure rather than occurring uniformly.",
    intuitiveExplanation:
      "Imagine qubits connected by springs (entanglement). When noise shakes the system, vibrations travel along the springs — not randomly through space. The spring topology determines which qubits feel the noise first and most strongly.",
    relatedTerms: ["structured_decoherence", "entanglement", "entanglement_error_correlation"],
    categoryId: "structured_decoherence",
  },
  {
    id: "asymmetry_index",
    name: "Asymmetry Index (AI)",
    formalDefinition:
      "Total Variation Distance from the uniform distribution over all 2ⁿ bitstrings: AI = TVD(P, U) = ½ Σᵢ |pᵢ − 1/2ⁿ|. Ranges from 0 (uniform/maximally noisy) to 1 (deterministic). Computed with full-support Jeffreys smoothing.",
    intuitiveExplanation:
      "How far the measurement distribution is from 'completely random'. AI = 0 means noise has destroyed all structure. AI = 1 means a single outcome dominates. Higher AI suggests the state retains structure despite noise.",
    symbol: "AI",
    relatedTerms: ["structure_score", "pathway_concentration_ratio", "structured_decoherence"],
    categoryId: "structured_decoherence",
  },
  {
    id: "structure_score",
    name: "Structure Score (SS)",
    formalDefinition:
      "Jensen-Shannon divergence between the observed distribution and a factorized null model (product of marginals): SS = JSD(P_observed || P_factorized). Ranges from 0 (no inter-qubit correlations) to 1 (maximum structure).",
    intuitiveExplanation:
      "Measures how much the qubits are correlated beyond what you'd expect if they were independent. SS = 0 means each qubit's noise is independent. SS > 0 means the noise pattern has genuine multi-qubit structure — evidence for structured decoherence.",
    symbol: "SS",
    relatedTerms: ["jensen_shannon_divergence", "asymmetry_index", "total_correlation"],
    categoryId: "structured_decoherence",
  },
  {
    id: "pathway_concentration_ratio",
    name: "Pathway Concentration Ratio (PCR)",
    formalDefinition:
      "The ratio of probability mass in the top quartile of outcomes to the bottom quartile: PCR = Σ(top 25% probabilities) / Σ(bottom 25% probabilities). Uses adaptive quartile boundaries based on the number of outcomes.",
    intuitiveExplanation:
      "How concentrated the decoherence is in a few pathways versus spread across many. High PCR means errors funnel through specific channels. Low PCR means errors spread uniformly — more like random fog than a directed river.",
    symbol: "PCR",
    relatedTerms: ["concentration_index", "asymmetry_index", "structured_decoherence"],
    categoryId: "structured_decoherence",
  },
  {
    id: "entanglement_error_correlation",
    name: "Entanglement-Error Correlation (EEC)",
    formalDefinition:
      "Pearson correlation between the entanglement topology matrix (adjacency structure of the state's entanglement graph) and the mutual information matrix (pairwise correlations in the noisy output). Tests whether errors follow entanglement bonds.",
    intuitiveExplanation:
      "Do errors flow along entanglement connections? EEC measures this directly by comparing the entanglement graph to the error pattern. High EEC means errors preferentially affect connected qubits — strong evidence for the Spring Network Model.",
    symbol: "EEC",
    relatedTerms: ["spring_network_model", "mutual_information", "structured_decoherence"],
    categoryId: "structured_decoherence",
  },
  {
    id: "temporal_pathway_stability",
    name: "Temporal Pathway Stability (TPS)",
    formalDefinition:
      "Spearman rank correlation of pathway probabilities across different noise conditions. Measures whether the relative ordering of decoherence pathways is preserved as noise strength varies. Uses transition matrices for multi-point analysis.",
    intuitiveExplanation:
      "Are the decoherence pathways stable or do they shift randomly with noise? High TPS means the same pathways dominate regardless of noise strength — the river keeps its channel. Low TPS means pathways are noise-dependent — more like random diffusion.",
    symbol: "TPS",
    relatedTerms: ["structured_decoherence", "pathway_concentration_ratio"],
    categoryId: "structured_decoherence",
  },
  {
    id: "complexity_emergence_score",
    name: "Complexity Emergence Score (CES)",
    formalDefinition:
      "Detects emergent complexity by fitting a logistic function to metric values across system sizes. Uses AIC model selection to distinguish genuine emergence from linear scaling. The inflection point identifies the critical system size.",
    intuitiveExplanation:
      "Does structured decoherence suddenly 'turn on' at a critical system size, or does it grow gradually? CES detects this threshold — like finding the critical temperature where water turns to ice. A sharp transition suggests a phase-like phenomenon.",
    symbol: "CES",
    relatedTerms: ["structured_decoherence", "structure_score"],
    categoryId: "structured_decoherence",
  },
  {
    id: "concentration_index",
    name: "Concentration Index (CI)",
    formalDefinition:
      "A Gini-like measure of inequality in the pathway probability distribution. CI = (2Σᵢ i·p_(i) − (n+1)) / n where p_(i) are sorted probabilities. Ranges from 0 (uniform) to 1 (maximally concentrated).",
    intuitiveExplanation:
      "How unequal the decoherence pathways are — like the Gini coefficient for wealth inequality, but for quantum noise. CI = 0 means all pathways are equally likely. CI near 1 means almost all probability flows through a few dominant pathways.",
    symbol: "CI",
    relatedTerms: ["pathway_concentration_ratio", "asymmetry_index", "structured_decoherence"],
    categoryId: "structured_decoherence",
  },
];
