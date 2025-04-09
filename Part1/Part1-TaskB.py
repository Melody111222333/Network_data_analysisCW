import pandas as pd
import networkx as nx
from itertools import combinations
import os

# Display full DataFrame output
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# === Step 1: Load data ===
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df[['page_name', 'thread_subject', 'username']]

# === Step 2: Build user co-occurrence network based on threads ===
def build_editor_network(df):
    G = nx.Graph()
    grouped = df.groupby(['page_name', 'thread_subject'])
    for _, group in grouped:
        users = group['username'].dropna().unique()
        for u1, u2 in combinations(users, 2):
            if G.has_edge(u1, u2):
                G[u1][u2]['weight'] += 1
            else:
                G.add_edge(u1, u2, weight=1)
    return G

# === Step 3: Compute network structure metrics ===
def analyze_network_metrics(G):
    metrics = {}
    largest_cc = max(nx.connected_components(G), key=len)
    G_cc = G.subgraph(largest_cc)

    # Approximate average path length (sampling)
    sample_nodes = list(G_cc.nodes())[:300]
    path_lengths = []
    for node in sample_nodes:
        lengths = nx.single_source_shortest_path_length(G_cc, node)
        path_lengths.extend(lengths.values())
    metrics['avg_path_length'] = sum(path_lengths) / len(path_lengths)

    # Additional metrics
    metrics['diameter'] = nx.diameter(G_cc)
    metrics['avg_clustering'] = nx.average_clustering(G)
    metrics['is_connected'] = nx.is_connected(G)
    metrics['num_components'] = nx.number_connected_components(G)
    metrics['nodes'] = G.number_of_nodes()
    metrics['edges'] = G.number_of_edges()
    return metrics

# === Step 4: Compare with random graph (small-world validation) ===
def compare_with_random(G, seed=42):
    n = G.number_of_nodes()
    m = G.number_of_edges()
    p = 2 * m / (n * (n - 1))  # edge density

    original_cc = nx.average_clustering(G)
    degrees = [d for _, d in G.degree()]
    original_avg_deg = sum(degrees) / len(degrees)

    R = nx.erdos_renyi_graph(n=n, p=p, seed=seed)
    rand_cc = nx.average_clustering(R)
    rand_deg = sum(dict(R.degree()).values()) / n

    return {
        "Original Clustering": round(original_cc, 4),
        "Random Clustering": round(rand_cc, 4),
        "Original Avg Degree": round(original_avg_deg, 2),
        "Random Avg Degree": round(rand_deg, 2)
    }

# === Main execution ===
def main():
    data_dir = "../Datasets"
    datasets = {
        "PROJECT_CHAT": os.path.join(data_dir, "PROJECT_CHAT.csv"),
        "PROPERTIES": os.path.join(data_dir, "PROPERTIES.csv"),
        "INTERWIKI_CONFLICT": os.path.join(data_dir, "INTERWIKI_CONFLICT.csv")
    }

    results = []
    random_comparison = []

    for name, path in datasets.items():
        print(f"\n Processing dataset: {name}")
        df = load_data(path)
        G = build_editor_network(df)

        # Network metrics
        metrics = analyze_network_metrics(G)
        metrics['dataset'] = name
        results.append(metrics)

        # Random graph comparison
        rand = compare_with_random(G)
        rand['Dataset'] = name
        random_comparison.append(rand)

    # Output results
    df_metrics = pd.DataFrame(results)
    print("\n Task B - Core network structure metrics:")
    print(df_metrics[['dataset', 'nodes', 'edges', 'is_connected', 'num_components',
                      'avg_path_length', 'diameter', 'avg_clustering']])

    df_compare = pd.DataFrame(random_comparison)
    print("\n Task B - Small-world validation (Original vs Random Graph):")
    print(df_compare[['Dataset', 'Original Clustering', 'Random Clustering',
                      'Original Avg Degree', 'Random Avg Degree']])

if __name__ == "__main__":
    main()

