import osmnx as ox
import geopandas as gpd

# Define the hotspot center coordinates (Easting, Northing in EPSG:27700)
center_easting, center_northing = 430000, 433500

# Convert to WGS84 (longitude, latitude) for OSMnx
gdf_point = gpd.GeoSeries.from_xy([center_easting], [center_northing], crs="EPSG:27700").to_crs(epsg=4326)
lon, lat = gdf_point.geometry.x[0], gdf_point.geometry.y[0]

G = ox.graph_from_point((lat, lon), dist=500, network_type="drive")

# Extract intersection nodes (network nodes)
nodes, _ = ox.graph_to_gdfs(G)

# Save to GeoJSON file for further analysis in Task B
nodes.to_file("network_nodes.geojson", driver="GeoJSON")
print("Intersection nodes saved as 'network_nodes.geojson'. Total nodes:", len(nodes))
