import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, box
import osmnx as ox
import networkx as nx
import os
import matplotlib.pyplot as plt

# === Step 1: Load traffic accident data ===
df = pd.read_csv("../Datasets/Traffic_accidents_2019_Leeds.csv")

# Construct GeoDataFrame using British National Grid (EPSG:27700)
gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(xy) for xy in zip(df["Grid Ref: Easting"], df["Grid Ref: Northing"])],
    crs="EPSG:27700"
)

# === Step 2: Identify the most accident-dense hotspot center ===
gdf['x'] = gdf.geometry.x
gdf['y'] = gdf.geometry.y
bins_x = pd.cut(gdf['x'], bins=100)
bins_y = pd.cut(gdf['y'], bins=100)
heatmap = gdf.groupby([bins_x, bins_y], observed=False).size().reset_index(name='count')
hot_cell = heatmap.sort_values('count', ascending=False).iloc[0]

# Extract the center coordinates of the hotspot cell
target_x = hot_cell['x'].mid
target_y = hot_cell['y'].mid
center_point = Point(target_x, target_y)

# Reproject to WGS84 (latitude & longitude)
gdf_center = gpd.GeoSeries([center_point], crs="EPSG:27700").to_crs(epsg=4326)
center_latlon = gdf_center.values[0]

north, south, east, west = ox.utils_geo.bbox_from_point((center_latlon.y, center_latlon.x), dist=500)
bbox = (north, south, east, west)
G = ox.graph_from_bbox(bbox, network_type="drive")

stats = ox.basic_stats(G)
G_proj = ox.project_graph(G)
edges = ox.graph_to_gdfs(G_proj, nodes=False)
area_km2 = edges.geometry.union_all().convex_hull.area / 1e6

node_density = stats['n'] / area_km2
edge_density = stats['m'] / area_km2
intersection_density = stats['intersection_count'] / area_km2

print("\n Hotspot center coordinate (WGS84):", center_latlon)
print(" Number of network nodes:", stats['n'])
print(" Average street segment length: {:.2f} m".format(stats['street_length_avg']))
print(" Network area: {:.2f} km²".format(area_km2))
print(" Node density: {:.2f} /km²".format(node_density))
print(" Edge density: {:.2f} /km²".format(edge_density))
print(" Intersection density: {:.2f} /km²".format(intersection_density))

is_planar, _ = nx.check_planarity(G)
print(" Is planar:", is_planar)

ox.plot_graph(G, bgcolor='white', node_color='red', edge_color='gray',save=True,filepath='../results/2A_taskd_osmnx_network.png',dpi=300,show=True )
