import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Read in census tract shape file
gdf_tract = gpd.read_file('tl_2019_37_tract.zip')

# Convert both gdf_urban and gdf_tract to the same projection
gdf_tract = gdf_tract.to_crs(epsg=32119)

# Read in the pharmacies data
pharmacies_df = pd.read_csv('pharmacies.csv')

# Create a GeoDataFrame from the pharmacies data
pharmacies_gdf = gpd.GeoDataFrame(
    pharmacies_df, 
    geometry=gpd.points_from_xy(pharmacies_df['X'], pharmacies_df['Y']),
    crs='EPSG:32119'
)

# Calculate accessability metric for each sampled point
n = 1 # power for accessability metric distance decay
sampled_points_gdf['accessability'] = sampled_points_gdf.geometry.apply(lambda x: sum(1/pharmacies_gdf.distance(x)))

# Plot the points on top of the tracts with accessability as the color
fig, ax = plt.subplots(figsize=(12, 12))
tracts.plot(ax=ax, color='white', edgecolor='black')
sampled_points_gdf.plot(ax=ax, column='accessability', cmap='coolwarm', markersize=0.5)
pharmacies_gdf.plot(ax=ax, color='black', markersize=0.5)
plt.show()
