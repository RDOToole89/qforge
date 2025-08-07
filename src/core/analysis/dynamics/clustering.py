# src/analysis/clustering.py

"""
Clustering analysis for quantum states and decoherence dynamics.

This module provides functions to cluster qubits based on their
correlation patterns, which can reveal the structure of entanglement
and decoherence dynamics in quantum states. Critical for understanding
structured decoherence patterns and noise characterization.
"""

import numpy as np
import logging
from typing import Dict, List, Optional
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


def analyze_decoherence_clusters(
    clusters_list: List[List[List[int]]],
    time_steps: List[float],
    pairwise_corrs_list: List[Dict]
) -> Dict:
    """
    Analyzes how qubit clusters evolve during decoherence.

    This function tracks how qubit clustering patterns change over time,
    revealing structured decoherence dynamics and noise characterization.

    Args:
        clusters_list: List of cluster assignments for each time step
        time_steps: List of time steps
        pairwise_corrs_list: List of pairwise correlations for each time step

    Returns:
        Dict: Analysis of cluster evolution during decoherence
    """
    if len(clusters_list) != len(time_steps) or len(clusters_list) != len(pairwise_corrs_list):
        logger.error("Mismatched data lengths for decoherence cluster analysis")
        return {"error": "Data length mismatch"}

    analysis = {
        "cluster_evolution": [],
        "cluster_stability": {},
        "decoherence_patterns": {},
        "noise_characterization": {}
    }

    # Analyze cluster evolution over time
    for i, (clusters, time_step, corrs) in enumerate(zip(clusters_list, time_steps, pairwise_corrs_list)):
        step_analysis = {
            "time_step": time_step,
            "num_clusters": len(clusters),
            "cluster_sizes": [len(cluster) for cluster in clusters],
            "total_correlation": np.mean(list(corrs.values())) if corrs else 0.0
        }
        analysis["cluster_evolution"].append(step_analysis)

    # Analyze cluster stability (which qubits stay together)
    if len(clusters_list) > 1:
        initial_clusters = clusters_list[0]
        final_clusters = clusters_list[-1]

        # Find qubits that stayed in same cluster
        stable_qubits = []
        for initial_cluster in initial_clusters:
            for final_cluster in final_clusters:
                common_qubits = set(initial_cluster) & set(final_cluster)
                if len(common_qubits) >= 2:  # At least 2 qubits stayed together
                    stable_qubits.extend(list(common_qubits))

        analysis["cluster_stability"] = {
            "stable_qubits": list(set(stable_qubits)),
            "stability_ratio": len(set(stable_qubits)) / sum(len(c) for c in initial_clusters)
        }

    # Characterize decoherence patterns
    if len(clusters_list) > 1:
        initial_cluster_count = len(clusters_list[0])
        final_cluster_count = len(clusters_list[-1])

        analysis["decoherence_patterns"] = {
            "cluster_fragmentation": final_cluster_count > initial_cluster_count,
            "fragmentation_ratio": final_cluster_count / max(initial_cluster_count, 1),
            "decoherence_rate": (final_cluster_count - initial_cluster_count) / len(time_steps)
        }

    # Noise characterization based on cluster patterns
    if len(clusters_list) > 1:
        avg_cluster_sizes = [np.mean([len(c) for c in clusters]) for clusters in clusters_list]
        cluster_size_variance = np.var(avg_cluster_sizes)

        analysis["noise_characterization"] = {
            "collective_noise": cluster_size_variance < 0.1,  # Clusters stay similar sizes
            "local_noise": cluster_size_variance > 0.5,       # Clusters fragment significantly
            "correlated_noise": any(len(c) >= 3 for clusters in clusters_list for c in clusters),  # Large clusters persist
            "noise_strength": cluster_size_variance
        }

    return analysis


def compute_cluster_decoherence_metrics(
    clusters: List[List[int]],
    pairwise_corrs: Dict,
    ideal_corrs: Optional[Dict] = None
) -> Dict:
    """
    Computes decoherence-specific metrics for qubit clusters.

    Args:
        clusters: List of qubit clusters
        pairwise_corrs: Current pairwise correlations
        ideal_corrs: Ideal correlations (for comparison)

    Returns:
        Dict: Decoherence metrics for clusters
    """
    metrics = {
        "cluster_purity": [],
        "cluster_fidelity": [],
        "decoherence_by_cluster": {},
        "entanglement_structure": {}
    }

    # Analyze each cluster
    for i, cluster in enumerate(clusters):
        if len(cluster) < 2:
            continue

        # Compute intra-cluster correlation strength
        cluster_corrs = []
        for q1 in cluster:
            for q2 in cluster:
                if q1 < q2 and (q1, q2) in pairwise_corrs:
                    cluster_corrs.append(pairwise_corrs[(q1, q2)])

        avg_cluster_corr = np.mean(cluster_corrs) if cluster_corrs else 0.0
        metrics["cluster_purity"].append(avg_cluster_corr)

        # Compare with ideal correlations if provided
        if ideal_corrs:
            ideal_cluster_corrs = []
            for q1 in cluster:
                for q2 in cluster:
                    if q1 < q2 and (q1, q2) in ideal_corrs:
                        ideal_cluster_corrs.append(ideal_corrs[(q1, q2)])

            if ideal_cluster_corrs:
                fidelity = np.mean(cluster_corrs) / np.mean(ideal_cluster_corrs) if np.mean(ideal_cluster_corrs) != 0 else 0
                metrics["cluster_fidelity"].append(fidelity)

        # Decoherence analysis per cluster
        metrics["decoherence_by_cluster"][f"cluster_{i}"] = {
            "size": len(cluster),
            "avg_correlation": avg_cluster_corr,
            "coherence": max(0, avg_cluster_corr)  # Higher correlation = more coherent
        }

    # Overall entanglement structure
    if metrics["cluster_purity"]:
        metrics["entanglement_structure"] = {
            "strongest_cluster": np.argmax(metrics["cluster_purity"]),
            "weakest_cluster": np.argmin(metrics["cluster_purity"]),
            "avg_cluster_strength": np.mean(metrics["cluster_purity"]),
            "cluster_uniformity": 1 - np.std(metrics["cluster_purity"])  # Higher = more uniform
        }

    return metrics
