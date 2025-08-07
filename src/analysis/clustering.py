# src/analysis/clustering.py

"""
Clustering analysis for quantum states.

This module provides functions to cluster qubits based on their
correlation patterns, which can reveal the structure of entanglement
in quantum states.
"""

import numpy as np
import logging
from typing import Dict, List
from sklearn.cluster import KMeans

logger = logging.getLogger("QuantumExperiment.Analysis.Clustering")


def cluster_qubits(
    pairwise_corrs: Dict, num_qubits: int, num_clusters: int = 2
) -> List[List[int]]:
    """
    Clusters qubits based on their pairwise correlation patterns using k-means.

    This function groups qubits that have similar correlation patterns,
    which can reveal the underlying structure of entanglement in the
    quantum state.

    Args:
        pairwise_corrs (Dict): Dictionary of pairwise correlations {(i,j): corr}.
        num_qubits (int): Number of qubits.
        num_clusters (int): Number of clusters to form (default: 2).

    Returns:
        List[List[int]]: List of clusters, where each cluster is a list of qubit indices.
    """
    # Create a feature vector for each qubit
    features = np.zeros((num_qubits, num_qubits))
    for (i, j), corr in pairwise_corrs.items():
        features[i, j] = corr
        features[j, i] = corr  # Symmetric matrix

    # Apply k-means clustering
    num_clusters = min(num_clusters, num_qubits)  # Ensure num_clusters <= num_qubits
    if num_clusters < 1:
        return [[i for i in range(num_qubits)]]  # Single cluster with all qubits
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(features)

    # Group qubits by cluster label
    clusters = [[] for _ in range(num_clusters)]
    for qubit_idx, label in enumerate(labels):
        clusters[label].append(qubit_idx)

    # Remove empty clusters
    clusters = [cluster for cluster in clusters if cluster]
    return clusters


def analyze_cluster_structure(clusters: List[List[int]], pairwise_corrs: Dict) -> Dict:
    """
    Analyzes the structure of qubit clusters.

    Args:
        clusters (List[List[int]]): List of qubit clusters.
        pairwise_corrs (Dict): Dictionary of pairwise correlations.

    Returns:
        Dict: Analysis of cluster structure.
    """
    analysis = {
        "num_clusters": len(clusters),
        "cluster_sizes": [len(cluster) for cluster in clusters],
        "intra_cluster_correlations": [],
        "inter_cluster_correlations": [],
    }

    # Analyze intra-cluster correlations
    for cluster in clusters:
        if len(cluster) < 2:
            analysis["intra_cluster_correlations"].append(0.0)
            continue

        cluster_corrs = []
        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                if (cluster[i], cluster[j]) in pairwise_corrs:
                    cluster_corrs.append(pairwise_corrs[(cluster[i], cluster[j])])
                elif (cluster[j], cluster[i]) in pairwise_corrs:
                    cluster_corrs.append(pairwise_corrs[(cluster[j], cluster[i])])

        avg_intra_corr = np.mean(cluster_corrs) if cluster_corrs else 0.0
        analysis["intra_cluster_correlations"].append(avg_intra_corr)

    # Analyze inter-cluster correlations
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            inter_corrs = []
            for qubit1 in clusters[i]:
                for qubit2 in clusters[j]:
                    if (qubit1, qubit2) in pairwise_corrs:
                        inter_corrs.append(pairwise_corrs[(qubit1, qubit2)])
                    elif (qubit2, qubit1) in pairwise_corrs:
                        inter_corrs.append(pairwise_corrs[(qubit2, qubit1)])

            avg_inter_corr = np.mean(inter_corrs) if inter_corrs else 0.0
            analysis["inter_cluster_correlations"].append(avg_inter_corr)

    return analysis


def find_optimal_clusters(
    pairwise_corrs: Dict, num_qubits: int, max_clusters: int = 5
) -> Dict:
    """
    Finds the optimal number of clusters using silhouette analysis.

    Args:
        pairwise_corrs (Dict): Dictionary of pairwise correlations.
        num_qubits (int): Number of qubits.
        max_clusters (int): Maximum number of clusters to try.

    Returns:
        Dict: Analysis with optimal number of clusters and scores.
    """
    from sklearn.metrics import silhouette_score

    # Create feature matrix
    features = np.zeros((num_qubits, num_qubits))
    for (i, j), corr in pairwise_corrs.items():
        features[i, j] = corr
        features[j, i] = corr

    scores = []
    clusterings = []

    for n_clusters in range(2, min(max_clusters + 1, num_qubits + 1)):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(features)

        # Compute silhouette score
        if len(set(labels)) > 1:  # Need at least 2 clusters for silhouette
            score = silhouette_score(features, labels)
            scores.append(score)
            clusterings.append(labels)
        else:
            scores.append(0.0)
            clusterings.append(labels)

    # Find optimal clustering
    if scores:
        optimal_idx = np.argmax(scores)
        optimal_n_clusters = optimal_idx + 2  # +2 because we started from 2 clusters
        optimal_labels = clusterings[optimal_idx]

        # Convert labels to clusters
        optimal_clusters = [[] for _ in range(optimal_n_clusters)]
        for qubit_idx, label in enumerate(optimal_labels):
            optimal_clusters[label].append(qubit_idx)
        optimal_clusters = [cluster for cluster in optimal_clusters if cluster]
    else:
        optimal_clusters = [[i for i in range(num_qubits)]]
        optimal_n_clusters = 1
        scores = [0.0]

    return {
        "optimal_n_clusters": optimal_n_clusters,
        "optimal_clusters": optimal_clusters,
        "silhouette_scores": scores,
        "best_score": max(scores) if scores else 0.0,
    }
