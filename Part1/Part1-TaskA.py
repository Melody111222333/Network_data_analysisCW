
import os
import pandas as pd
import networkx as nx
from itertools import combinations
import matplotlib.pyplot as plt
import os

def load_data(file_path):
    df = pd.read_csv(file_path)
    return df[['page_name', 'thread_subject', 'username']]

def build_editor_network(df):
    G = nx.Graph()
    grouped = df.groupby(['page_name', 'thread_subject'])
    for _, group in grouped:
        users =- group['username'].dropna().unique()
        for u1, u2 in combinations(users, 2):
            if G.has_edge(u1, u2):
                G[u1][u2]['weight'] += 1
            else:
                G.add_edge(u1, u2, weight=1)
    return G

def analyze_graph(G, dataset_name):
    print(f"\n--- {dataset_name} ---")
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
    print(f"Average degree: {avg_degree:.2f}")
    print(f"Density: {nx.density(G):.5f}")

def visualize_subgraph(G, dataset_name, max_nodes=50, save_path=None):
    import matplotlib.pyplot as plt

    sub_nodes = list(G.nodes)[:max_nodes]
    subgraph = G.subgraph(sub_nodes)

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(subgraph, seed=42)
    nx.draw_networkx_nodes(subgraph, pos, node_size=300, node_color='lightblue')
    nx.draw_networkx_edges(subgraph, pos, alpha=0.5)
    nx.draw_networkx_labels(subgraph, pos, font_size=8)
    plt.title(f"{dataset_name} Subgraph Visualization (Top {max_nodes} Users)", fontsize=14)
    plt.axis('off')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"The figure has been saved to: {save_path}")

    plt.show()


def main():
    data_dir = "../Datasets"
    datasets = {
        "PROJECT_CHAT": os.path.join(data_dir, "PROJECT_CHAT.csv"),
        "PROPERTIES": os.path.join(data_dir, "PROPERTIES.csv"),
        "INTERWIKI_CONFLICT": os.path.join(data_dir, "INTERWIKI_CONFLICT.csv"),
    }

    graphs = {}

    for name, path in datasets.items():
        df = load_data(path)
        G = build_editor_network(df)
        analyze_graph(G, name)
        graphs[name] = G

    return graphs

import os

if __name__ == "__main__":
    graphs = main()
    save_path = "../results/1A_interwiki_conflict_subgraph.png"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    visualize_subgraph(graphs["INTERWIKI_CONFLICT"], "INTERWIKI_CONFLICT", save_path=save_path)
