import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import Point
from libpysal.weights import DistanceBand
from esda.moran import Moran

df = pd.read_csv("../Datasets/Traffic_accidents_2019_Leeds.csv")
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["Grid Ref: Easting"], df["Grid Ref: Northing"]), crs="EPSG:27700")

# Define hotspot center and 1km x 1km buffer area
center_point = Point(430000, 433500)
buffer_polygon = center_point.buffer(500)
bbox = gpd.GeoDataFrame({'geometry': [buffer_polygon]}, crs="EPSG:27700")
gdf_clip = gpd.clip(gdf, bbox)

gdf_nodes = gpd.read_file("network_nodes.geojson")
gdf_nodes = gdf_nodes.to_crs(gdf_clip.crs)

# Calculate distance to nearest intersection
gdf_clip.loc[:, "nearest_dist"] = gdf_clip.geometry.apply(lambda x: gdf_nodes.distance(x).min())

gdf_clip_proj = gdf_clip.to_crs(epsg=3857)
coords = list(zip(gdf_clip_proj.geometry.x, gdf_clip_proj.geometry.y))
w = DistanceBand(coords, threshold=200, binary=True)
moran = Moran(gdf_clip_proj["Grid Ref: Easting"], w)

# Summary statistics
num_accidents = len(gdf_clip)
avg_dist = gdf_clip["nearest_dist"].mean()
max_dist = gdf_clip["nearest_dist"].max()
min_dist = gdf_clip["nearest_dist"].min()

print("Number of accident points:", num_accidents)
print("Moran's I:", moran.I)
print("p-value:", moran.p_norm)
print("Average distance to nearest intersection:", avg_dist)
print("Maximum distance:", max_dist)
print("Minimum distance:", min_dist)

# Save results to a .txt file
with open("../Results/Part2_taskb_results.txt", "w") as f:
    f.write(f"Number of accident points: {num_accidents}\n")
    f.write(f"Moran's I: {moran.I:.4f}\n")
    f.write(f"p-value: {moran.p_norm:.4e}\n")
    f.write(f"Average distance to nearest intersection: {avg_dist:.2f} m\n")
    f.write(f"Maximum distance: {max_dist:.2f} m\n")
    f.write(f"Minimum distance: {min_dist:.2f} m\n")

plt.figure(figsize=(8, 4))
sns.histplot(gdf_clip["nearest_dist"], bins=20, kde=True, color="steelblue", edgecolor="black")
plt.xlabel("Distance to Nearest Intersection (meters)")
plt.ylabel("Number of Accidents")
plt.title("Distribution of Accident-to-Intersection Distances")
plt.grid(True)
plt.tight_layout()

# Save the figure
output_path = "../Results/2B_Figure_Distance_Distribution.png"
plt.savefig(output_path)
print(f"The figure has been saved to: {output_path}")

plt.show()
