# src/analysis/transitions.py

"""
Error transition analysis for quantum states.

This module provides functions to analyze error transitions in quantum states,
including transition probabilities and error dynamics.
"""

import numpy as np
import logging
from typing import Dict, List
import networkx as nx

logger = logging.getLogger("QuantumExperiment.Analysis.Transitions")


def compute_error_transitions(counts_list: List[Dict], time_steps: List[float]) -> Dict:
    """
    Computes error transition probabilities between quantum states.

    Args:
        counts_list (List[Dict]): List of measurement counts for each timestep.
        time_steps (List[float]): List of timesteps.

    Returns:
        Dict: Transition analysis including transition graph and probabilities.
    """
    if not counts_list or len(counts_list) < 2:
        return {"error": "Insufficient data for transition analysis"}

    num_qubits = len(next(iter(counts_list[0].keys())))
    states = [format(i, f"0{num_qubits}b") for i in range(2**num_qubits)]

    # Create transition graph
    G = nx.DiGraph()
    for state in states:
        G.add_node(state)

    # Compute transition probabilities
    shots = sum(counts_list[0].values())
    transition_data = {}

    for t in range(len(counts_list) - 1):
        counts_t = counts_list[t]
        counts_t1 = counts_list[t + 1]
        time_step = time_steps[t]

        transitions = {}
        for state in states:
            prob_t = counts_t.get(state, 0) / shots
            for next_state in states:
                prob_t1 = counts_t1.get(next_state, 0) / shots
                if prob_t > 0 and prob_t1 > 0 and state != next_state:
                    transition_prob = prob_t1 / prob_t
                    if transition_prob > 0.01:  # Threshold for significant transitions
                        transitions[(state, next_state)] = transition_prob
                        G.add_edge(
                            state, next_state, weight=transition_prob, t=time_step
                        )

        transition_data[time_step] = transitions

    # Analyze transition patterns
    analysis = {
        "num_transitions": len(G.edges()),
        "num_states": len(states),
        "transition_data": transition_data,
        "graph": G,
    }

    # Compute transition statistics
    if G.edges():
        weights = [G[u][v]["weight"] for u, v in G.edges()]
        analysis["avg_transition_prob"] = np.mean(weights)
        analysis["max_transition_prob"] = max(weights)
        analysis["min_transition_prob"] = min(weights)
    else:
        analysis["avg_transition_prob"] = 0.0
        analysis["max_transition_prob"] = 0.0
        analysis["min_transition_prob"] = 0.0

    return analysis


def analyze_transition_dynamics(transition_data: Dict, time_steps: List[float]) -> Dict:
    """
    Analyzes the dynamics of error transitions over time.

    Args:
        transition_data (Dict): Transition data from compute_error_transitions.
        time_steps (List[float]): List of timesteps.

    Returns:
        Dict: Analysis of transition dynamics.
    """
    if "error" in transition_data:
        return transition_data

    analysis = {
        "transition_rates": [],
        "state_populations": {},
        "error_accumulation": {},
    }

    # Analyze transition rates over time
    for time_step in time_steps[:-1]:
        if time_step in transition_data:
            transitions = transition_data[time_step]
            if transitions:
                avg_rate = np.mean(list(transitions.values()))
                analysis["transition_rates"].append(
                    {
                        "time": time_step,
                        "avg_rate": avg_rate,
                        "num_transitions": len(transitions),
                    }
                )

    # Analyze state populations
    states = (
        list(transition_data[time_steps[0]].keys())
        if time_steps and time_steps[0] in transition_data
        else []
    )
    for state in states:
        populations = []
        for time_step in time_steps:
            if time_step in transition_data:
                # Find transitions to this state
                incoming = [
                    prob
                    for (s1, s2), prob in transition_data[time_step].items()
                    if s2 == state
                ]
                if incoming:
                    populations.append(np.mean(incoming))
                else:
                    populations.append(0.0)
        analysis["state_populations"][state] = populations

    # Analyze error accumulation
    if analysis["transition_rates"]:
        rates = [tr["avg_rate"] for tr in analysis["transition_rates"]]
        cumulative_error = np.cumsum(rates)
        analysis["error_accumulation"] = {
            "rates": rates,
            "cumulative": cumulative_error.tolist(),
            "final_error": cumulative_error[-1] if cumulative_error.size > 0 else 0.0,
        }

    return analysis


def find_dominant_transitions(
    transition_data: Dict, threshold: float = 0.1
) -> List[tuple]:
    """
    Finds the dominant error transitions above a threshold.

    Args:
        transition_data (Dict): Transition data from compute_error_transitions.
        threshold (float): Probability threshold for dominant transitions.

    Returns:
        List[tuple]: List of dominant transitions as (state1, state2, probability).
    """
    dominant_transitions = []

    for time_step, transitions in transition_data.items():
        for (state1, state2), prob in transitions.items():
            if prob > threshold:
                dominant_transitions.append((state1, state2, prob, time_step))

    # Sort by probability (highest first)
    dominant_transitions.sort(key=lambda x: x[2], reverse=True)
    return dominant_transitions


def compute_transition_entropy(
    transition_data: Dict, time_steps: List[float]
) -> List[float]:
    """
    Computes the entropy of transition probabilities over time.

    Args:
        transition_data (Dict): Transition data from compute_error_transitions.
        time_steps (List[float]): List of timesteps.

    Returns:
        List[float]: Entropy values for each timestep.
    """
    entropies = []

    for time_step in time_steps[:-1]:
        if time_step in transition_data:
            transitions = transition_data[time_step]
            if transitions:
                probs = list(transitions.values())
                # Normalize probabilities
                total_prob = sum(probs)
                if total_prob > 0:
                    normalized_probs = [p / total_prob for p in probs]
                    # Compute entropy: -sum(p * log(p))
                    entropy = -sum(p * np.log(p) for p in normalized_probs if p > 0)
                    entropies.append(entropy)
                else:
                    entropies.append(0.0)
            else:
                entropies.append(0.0)
        else:
            entropies.append(0.0)

    return entropies
