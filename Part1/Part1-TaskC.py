import networkx as nx
import random
import matplotlib.pyplot as plt
import pandas as pd
from itertools import combinations

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

# === Spread probability estimation ===
def calculate_spread_probability(G, node1, node2):
    if nx.has_path(G, node1, node2):
        shortest_path = nx.shortest_path_length(G, node1, node2)
        return 1 / (shortest_path + 1)  # Shorter path → higher probability
    return 0

# === Generate priority check list ===
def get_priority_list(G):
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)

    scores = {node: (betweenness[node] + closeness[node]) / 2 for node in G.nodes()}
    sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [node for node, _ in sorted_nodes]

# === SIR model simulation ===
def sir_simulation(G, initial_infected, beta=0.3, gamma=0.1, steps=10):
    status = {node: "S" for node in G.nodes()}
    for node in initial_infected:
        status[node] = "I"

    infected_counts = []

    for _ in range(steps):
        new_status = status.copy()

        for node in G.nodes():
            if status[node] == "I":
                # Try to infect neighbors
                for neighbor in G.neighbors(node):
                    if status[neighbor] == "S" and random.random() < beta:
                        new_status[neighbor] = "I"
                # Recovery process
                if random.random() < gamma:
                    new_status[node] = "R"

        status = new_status
        infected_counts.append(sum(1 for s in status.values() if s == "I"))

    return infected_counts

# === Main execution ===
def main():
    data_path = "../Datasets/PROJECT_CHAT.csv"
    df = pd.read_csv(data_path)
    G = build_editor_network(df)

    # Randomly select 2 users for spread probability estimation
    random_users = random.sample(list(G.nodes()), 2)
    probability = calculate_spread_probability(G, random_users[0], random_users[1])
    print(f"Spread probability ({random_users[0]} → {random_users[1]}): {probability:.4f}")

    # Get priority user list
    priority_list = get_priority_list(G)
    print("Priority check list (Top 10):", priority_list[:10])

    # Run SIR simulation
    initial_infected = random.sample(list(G.nodes()), 5)
    spread_results = sir_simulation(G, initial_infected)

    # Plot infection curve
    plt.plot(spread_results, marker='o')
    plt.xlabel("Time Step")
    plt.ylabel("Number of Infected Nodes")
    plt.title("SIR Model Simulation")
    plt.tight_layout()
    plt.savefig("../results/1C_sir_infection_curve.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    main()
