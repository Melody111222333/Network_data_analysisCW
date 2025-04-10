import osmnx as ox
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
import random

# Step 1: Load full Leeds road network
ox.settings.log_console = True
ox.settings.use_cache = True
G = ox.graph_from_place("Leeds, UK", network_type="drive")
nodes, edges = ox.graph_to_gdfs(G)

# Step 2: Define 4 seed points (longitude, latitude)
seeds = [
    (-1.575, 53.822),  # West Leeds
    (-1.470, 53.825),  # NE Leeds
    (-1.540, 53.760),  # South
    (-1.510, 53.800),  # Central
]

# Step 3: Assign Voronoi region to each node
seed_points = [Point(xy) for xy in seeds]
vor = Voronoi(seeds)
node_coords = np.array([(geom.xy[0][0], geom.xy[1][0]) for geom in nodes.geometry])
node_regions = [np.argmin([Point(c).distance(Point(xy)) for xy in seeds]) for c in node_coords]
nodes['region'] = node_regions

# Step 4: For each region, find a loop path ~42km (greedy random search)
def find_loop(G, start_node, target_length_km=42, max_attempts=100):
    path = [start_node]
    total_length = 0
    for _ in range(max_attempts):
        neighbors = list(G.neighbors(path[-1]))
        random.shuffle(neighbors)
        for n in neighbors:
            if n not in path:
                edge_data = G.get_edge_data(path[-1], n)[0]
                length = edge_data.get('length', 0) / 1000  # meters → km
                if total_length + length > target_length_km * 1.05:
                    continue
                path.append(n)
                total_length += length
                if total_length >= target_length_km * 0.95 and nx.has_path(G, n, start_node):
                    back_path = nx.shortest_path(G, n, start_node, weight='length')
                    back_len = sum(G.get_edge_data(u, v)[0]['length'] for u, v in zip(back_path[:-1], back_path[1:])) / 1000
                    if total_length + back_len <= target_length_km * 1.1:
                        path.extend(back_path[1:])
                        total_length += back_len
                        return path, total_length
                break
    return None, 0

fig, ax = ox.plot_graph(G, show=False, close=False)
colors = ['red', 'blue', 'green', 'orange']
for i in range(4):
    sub_nodes = nodes[nodes['region'] == i]
    subgraph = G.subgraph(sub_nodes.index)
    try:
        start_node = sub_nodes.sample(1).index[0]
        loop_path, loop_len = find_loop(subgraph, start_node)
        if loop_path:
            ox.plot_graph_route(subgraph, loop_path, route_color=colors[i], ax=ax, show=False, close=False)
            print(f"Region {i}: Loop path found. Length ≈ {loop_len:.2f} km")
        else:
            print(f"Region {i}: No loop found.")
    except:
        print(f"Region {i}: Error during path search.")

# Plot Voronoi diagram
voronoi_plot_2d(vor, ax=ax, show_vertices=False, line_colors='gray')
plt.title("Voronoi Regions & 42km Loop Paths in Leeds")
plt.tight_layout()
fig.savefig("../Results/2C_voronoi_marathon_paths_leeds.png", dpi=300)
print("Image saved as 'voronoi_marathon_paths_leeds.png'")

plt.show()
