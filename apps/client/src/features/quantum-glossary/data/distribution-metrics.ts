import type { GlossaryCategory, GlossaryTerm } from "../types";
import { viz } from "@/src/design/tokens";

export const category: GlossaryCategory = {
  id: "distribution_metrics",
  name: "Distribution Metrics",
  icon: "git-branch",
  color: viz.gate.amber,
  description: "Statistical metrics the framework computes on measurement outcome distributions",
};

export const terms: GlossaryTerm[] = [
  {
    id: "asymmetry_index",
    name: "Asymmetry Index (AI)",
    formalDefinition:
      "Total Variation Distance from the uniform distribution over all 2ⁿ bitstrings: AI = TVD(P, U) = ½ Σᵢ |pᵢ − 1/2ⁿ|. Ranges from 0 (uniform) toward 1 (concentrated on few outcomes). Computed with full-support Jeffreys smoothing.",
    intuitiveExplanation:
      "How far the measurement distribution is from 'completely flat'. AI = 0 means every outcome is equally likely. Higher AI means the distribution is concentrated on fewer outcomes.",
    symbol: "AI",
    keyEquation: "\\text{AI} = \\frac{1}{2} \\sum_{i=0}^{2^n-1} |p_i - 2^{-n}|",
    formulaExplanation:
      "Total Variation Distance from the uniform distribution. Sums the absolute differences between each observed probability and 1/2\u207f. AI = 0 means the distribution is uniform; larger AI means probability is concentrated in fewer outcomes.",
    relatedTerms: ["structure_score", "pathway_concentration_ratio", "concentration_index"],
    categoryId: "distribution_metrics",
  },
  {
    id: "structure_score",
    name: "Structure Score (SS)",
    formalDefinition:
      "Jensen-Shannon divergence between the observed distribution and a factorized null model (product of marginals): SS = JSD(P_observed || P_factorized). Ranges from 0 (no inter-qubit correlations) to 1 (maximal divergence).",
    intuitiveExplanation:
      "Measures how much the qubits are correlated beyond what you'd expect if they were independent. SS = 0 means the distribution matches the product of its single-qubit marginals. SS > 0 means the outcomes carry genuine multi-qubit correlations.",
    symbol: "SS",
    keyEquation: "\\text{SS} = \\text{JSD}(P_{\\text{obs}} \\| P_{\\text{fact}}), \\quad P_{\\text{fact}} = \\prod_i P_i",
    formulaExplanation:
      "Jensen-Shannon divergence between the observed distribution and the product of its marginals. If qubits were statistically independent, these would match (SS = 0). Nonzero SS quantifies the multi-qubit correlations in the measured counts.",
    relatedTerms: ["jensen_shannon_divergence", "asymmetry_index", "total_correlation"],
    categoryId: "distribution_metrics",
  },
  {
    id: "pathway_concentration_ratio",
    name: "Pathway Concentration Ratio (PCR)",
    formalDefinition:
      "The ratio of probability mass in the top quartile of outcomes to the bottom quartile: PCR = Σ(top 25% probabilities) / Σ(bottom 25% probabilities). Uses adaptive quartile boundaries based on the number of outcomes.",
    intuitiveExplanation:
      "How concentrated the distribution is in its most likely outcomes versus its least likely ones. PCR = 1 means uniform; large PCR means a few outcomes dominate the counts.",
    symbol: "PCR",
    keyEquation: "\\text{PCR} = \\frac{\\sum_{\\text{top 25\\%}} p_i}{\\sum_{\\text{bottom 25\\%}} p_i}",
    formulaExplanation:
      "Ratio of probability mass in the most-likely quarter of outcomes to the least-likely quarter. PCR = 1 for a uniform distribution; large PCR means probability is concentrated in a few dominant outcomes.",
    relatedTerms: ["concentration_index", "asymmetry_index", "structure_score"],
    categoryId: "distribution_metrics",
  },
  {
    id: "entanglement_error_correlation",
    name: "Entanglement-Error Correlation (EEC)",
    formalDefinition:
      "Pearson correlation between the entanglement topology matrix (adjacency structure of the prepared state's entanglement graph) and the mutual information matrix (pairwise correlations in the noisy output).",
    intuitiveExplanation:
      "Compares two matrices: which qubit pairs are entangled by the preparation circuit, and which qubit pairs show correlated outcomes in the noisy measurement data. High EEC means the pairwise output correlations line up with the preparation topology.",
    symbol: "EEC",
    keyEquation: "\\text{EEC} = \\text{Pearson}(\\mathbf{A}_{\\text{topo}}, \\mathbf{M}_{\\text{MI}})",
    formulaExplanation:
      "Pearson correlation between the entanglement adjacency matrix and the pairwise mutual information matrix of the measured counts. It quantifies how similar the two matrices are, entry by entry.",
    relatedTerms: ["mutual_information", "entanglement", "structure_score"],
    categoryId: "distribution_metrics",
  },
  {
    id: "temporal_pathway_stability",
    name: "Temporal Pathway Stability (TPS)",
    formalDefinition:
      "Spearman rank correlation of outcome probabilities across different noise conditions. Measures whether the relative ordering of outcomes is preserved as noise strength varies. Uses transition matrices for multi-point analysis.",
    intuitiveExplanation:
      "Compares the ranking of outcomes between conditions. High TPS means the same outcomes stay the most likely as the noise level changes; low TPS means the ordering reshuffles between conditions.",
    symbol: "TPS",
    relatedTerms: ["pathway_concentration_ratio", "structure_score"],
    categoryId: "distribution_metrics",
  },
  {
    id: "complexity_emergence_score",
    name: "Complexity Emergence Score (CES)",
    formalDefinition:
      "Fits a logistic function to metric values across system sizes and compares it against a linear fit using AIC model selection. The inflection point of the logistic fit identifies the system size where the metric rises fastest.",
    intuitiveExplanation:
      "Does a metric grow gradually with system size, or rise sharply around some size? CES fits both shapes to the data and reports which fits better, and where the sharp rise (if any) is centered.",
    symbol: "CES",
    relatedTerms: ["structure_score", "total_correlation"],
    categoryId: "distribution_metrics",
  },
  {
    id: "concentration_index",
    name: "Concentration Index (CI)",
    formalDefinition:
      "The canonical name for the Pathway Concentration Ratio: the ratio of probability mass in the top quartile of outcomes to the bottom quartile. Ranges from 1 (uniform) upward. The analysis extras also report a Gini coefficient of the sorted probabilities as a bounded companion measure.",
    intuitiveExplanation:
      "How unequal the outcome probabilities are. CI = 1 means all outcomes are equally likely; large CI means a few outcomes hold most of the probability. In this framework it is computed identically to the Pathway Concentration Ratio.",
    symbol: "CI",
    keyEquation: "\\text{CI} = \\frac{\\sum_{\\text{top 25\\%}} p_i}{\\sum_{\\text{bottom 25\\%}} p_i}",
    formulaExplanation:
      "Sort the outcome probabilities, sum the most-likely quarter, and divide by the sum of the least-likely quarter. Equal to 1 for a uniform distribution and grows as probability concentrates.",
    relatedTerms: ["pathway_concentration_ratio", "asymmetry_index", "structure_score"],
    categoryId: "distribution_metrics",
  },
  {
    id: "delta_cov_fingerprint",
    name: "ΔCov Matrix",
    formalDefinition:
      "The excess covariance matrix ΔCov = Cov(noisy) − Cov(ideal) of the qubit outcomes, often flattened to the n(n−1)/2-dimensional vector of upper-triangle pairwise entries. The direction of the vector records which qubit pairs changed; the magnitude records by how much.",
    intuitiveExplanation:
      "A compact summary of how noise changed the pairwise correlations of a state. Instead of a single number ('how noisy'), it's a matrix showing WHICH qubit pairs gained or lost correlation. The visualizer displays it as a heatmap at each circuit step.",
    symbol: "ΔCov",
    keyEquation:
      "\\Delta\\text{Cov} = \\text{Cov}(\\text{noisy}) - \\text{Cov}(\\text{ideal}) \\in \\mathbb{R}^{n(n-1)/2}",
    formulaExplanation:
      "Subtract the ideal covariance matrix from the noisy one to isolate what noise changed. The upper triangle gives a vector with one entry per qubit pair — for 6 qubits that's 15 entries.",
    relatedTerms: ["covariance_matrix", "mutual_information", "structure_score"],
    categoryId: "distribution_metrics",
  },
];
