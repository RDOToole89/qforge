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
    edges = build_hypergraph_edges(correlation_data, config=cfg)
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
    for _, (nodes, props) in edges.items():
        node_list = list(nodes)
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                u, v = node_list[i], node_list[j]
                w = float(props.get("weight", 1.0))
                G.add_edge(u, v, weight=abs(w))

    pos = nx.spring_layout(G, seed=42)
    widths = [1 + 4 * d.get("weight", 1.0) for _, _, d in G.edges(data=True)]
    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw_networkx(G, pos=pos, width=widths, node_color="#4C78A8", ax=ax)
    title = f"Hypergraph ({state_type or 'state'})"
    if noise_type:
        title += f" with {noise_type} noise"
    ax.set_title(title)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
