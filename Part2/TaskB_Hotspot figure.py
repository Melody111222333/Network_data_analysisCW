import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, box
from pyproj import Transformer

df = pd.read_csv("../Datasets/Traffic_accidents_2019_Leeds.csv")

gdf_accidents = gpd.GeoDataFrame(
    df,
    geometry=[Point(xy) for xy in zip(df["Grid Ref: Easting"], df["Grid Ref: Northing"])],
    crs="EPSG:27700"
)

center_easting = 430000
center_northing = 433500
buffer = 500  # Radius = 500 meters → 1km x 1km square

# Define the bounding box (hotspot area)
bbox = box(center_easting - buffer, center_northing - buffer,
           center_easting + buffer, center_northing + buffer)

# Filter accidents that fall within the hotspot box
gdf_hotspot_accidents = gdf_accidents[gdf_accidents.geometry.within(bbox)]
gdf_hotspot_accidents = gdf_hotspot_accidents.to_crs(epsg=4326)  # Convert to WGS84 for plotting

gdf_intersections = gpd.read_file("network_nodes.geojson").to_crs(epsg=4326)

transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
x0, y0 = transformer.transform(center_easting - buffer, center_northing - buffer)
x1, y1 = transformer.transform(center_easting + buffer, center_northing - buffer)
x2, y2 = transformer.transform(center_easting + buffer, center_northing + buffer)
x3, y3 = transformer.transform(center_easting - buffer, center_northing + buffer)

fig, ax = plt.subplots(figsize=(10, 10))

gdf_hotspot_accidents.plot(ax=ax, color="red", markersize=30, label="Accidents")

gdf_intersections.plot(ax=ax, color="blue", markersize=25, label="Intersections")

bbox_xs = [x0, x1, x2, x3, x0]
bbox_ys = [y0, y1, y2, y3, y0]
ax.plot(bbox_xs, bbox_ys, color="gray", linewidth=2, label="Hotspot Boundary")

# Set title and legend
ax.set_title("Accident Distribution and Intersections in Hotspot Area", fontsize=14)
ax.legend()
ax.set_axis_off()
plt.tight_layout()

# Save the figure
output_path = "../Results/2B_Accident Distribution and Intersections in Hotspot Area.png"
plt.savefig(output_path)
print(f"The figure has been saved to: {output_path}")
plt.show()
