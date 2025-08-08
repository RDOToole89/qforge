from __future__ import annotations

from typing import Mapping, Any, Optional

import matplotlib.pyplot as plt
import networkx as nx

from src.visualization.analysis.hypergraph import build_hypergraph_edges


def draw_hypergraph(
    correlation_data: Mapping[str, int] | Mapping[str, float],
    *,
    state_type: Optional[str],
    noise_type: Optional[str],
    save_path: str,
    config: Mapping[str, Any] | None = None,
) -> None:
    cfg = dict(config or {})
    # Build edges; if none, take top-k strongest pairwise as a fallback
    edges = build_hypergraph_edges(correlation_data, config=cfg, top_k_fallback=3)
    if not edges:
        fig = plt.figure(figsize=(6, 4))
        plt.title("No significant correlations found")
        plt.text(0.5, 0.5, "No edges to plot", ha="center", va="center")
        plt.axis("off")
        fig.tight_layout()
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        return

    G = nx.Graph()
    used_fallback = False
    for _, (nodes, props) in edges.items():
        node_list = list(nodes)
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                u, v = node_list[i], node_list[j]
                w = float(props.get("weight", 1.0))
                G.add_edge(u, v, weight=abs(w))
        if props.get("fallback"):
            used_fallback = True

    pos = nx.spring_layout(G, seed=42)
    widths = [1 + 4 * d.get("weight", 1.0) for _, _, d in G.edges(data=True)]
    fig, ax = plt.subplots(figsize=(8, 6))
    # Slightly varied node colors for readability
    palette = ["#4C78A8", "#72B7B2", "#54A24B", "#E45756", "#F58518", "#B279A2"]
    node_colors = [palette[i % len(palette)] for i, _ in enumerate(G.nodes)]
    nx.draw_networkx(
        G,
        pos=pos,
        width=widths,
        node_color=node_colors,
        node_size=700,
        font_size=12,
        font_color="#1f2937",
        edgecolors="#2F3B52",
        linewidths=1.0,
        ax=ax,
    )
    # Edge labels with correlation weight
    edge_labels = {
        (u, v): f"{d.get('weight', 0):.2f}" for u, v, d in G.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        G, pos=pos, edge_labels=edge_labels, font_size=9, ax=ax
    )
    title = f"Correlation graph ({state_type or 'state'})"
    if noise_type:
        title += f" with {noise_type} noise"
    if used_fallback:
        title += " — top correlations"
    ax.set_title(title)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
