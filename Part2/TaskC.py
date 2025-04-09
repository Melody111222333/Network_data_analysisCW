import networkx as nx
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import random
import os
from shapely.geometry import Point
import matplotlib.cm as cm
import numpy as np

# Load network nodes
nodes_gdf = gpd.read_file("network_nodes.geojson")
nodes_gdf = nodes_gdf.to_crs(epsg=27700)

# Create graph from nodes
G = nx.Graph()
for idx, row in nodes_gdf.iterrows():
    G.add_node(idx, osmid=row["osmid"], x=row.geometry.x, y=row.geometry.y, geometry=row.geometry)

# Add edges between nodes that are within 100m
for i, node1 in nodes_gdf.iterrows():
    for j, node2 in nodes_gdf.iterrows():
        if i != j:
            dist = node1.geometry.distance(node2.geometry)
            if dist < 100:
                G.add_edge(i, j, weight=dist)

# Load traffic accident data
accidents_df = pd.read_csv("../Datasets/Traffic_accidents_2019_Leeds.csv")
accident_gdf = gpd.GeoDataFrame(accidents_df,
    geometry=gpd.points_from_xy(accidents_df["Grid Ref: Easting"], accidents_df["Grid Ref: Northing"]),
    crs="EPSG:27700"
)

# Filter accidents within the hotspot area (buffer of 500m around a central point)
hotspot_center = Point(430000, 433500)
hotspot_area = hotspot_center.buffer(500)
accident_hotspot = accident_gdf[accident_gdf.geometry.within(hotspot_area)]

# Select seed nodes: find nearest graph node to each accident
def find_nearest_node(point, nodes_gdf):
    distances = nodes_gdf.geometry.distance(point)
    return distances.idxmin()

seed_nodes = set()
for pt in accident_hotspot.geometry:
    idx = find_nearest_node(pt, nodes_gdf)
    seed_nodes.add(idx)

# Independent Cascade model
def run_ic_model(G, seeds, p=0.1, max_steps=10):
    active = set(seeds)
    new_active = set(seeds)
    activation_timeline = [list(new_active)]

    for _ in range(max_steps):
        next_active = set()
        for node in new_active:
            for neighbor in G.neighbors(node):
                if neighbor not in active and random.random() < p:
                    next_active.add(neighbor)
        if not next_active:
            break
        active.update(next_active)
        activation_timeline.append(list(next_active))

    return activation_timeline

# Run the model
random.seed(42)
timeline = run_ic_model(G, seed_nodes, p=0.2, max_steps=7)

# Positioning nodes for visualization
pos = {idx: (data["x"], data["y"]) for idx, data in G.nodes(data=True)}

# Create the color map
cmap = cm.get_cmap('viridis', len(timeline))  # N discrete colors

# Plot the graph
plt.figure(figsize=(10, 10))
for step, nodes in enumerate(timeline):
    color = cmap(step)  # Get distinct color for each step
    nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=[color], label=f"Step {step}", node_size=40)

# Draw edges
nx.draw_networkx_edges(G, pos, alpha=0.3)

# Set plot title and show
plt.title("Independent Cascade Model Spread from Accident Hotspot")
plt.axis('off')
plt.legend()
plt.tight_layout()

# Save the figure
output_path = "../Results/2C_IC_model_propagation.png"
plt.savefig(output_path)
print(f"IC Model figure saved at: {output_path}")
plt.show()

# Save results
with open("../Results/2C_activation_log.txt", "w") as f:
    for i, step_nodes in enumerate(timeline):
        f.write(f"Step {i}: {step_nodes}\n")
