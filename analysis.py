import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Read in the pharmacies data
pharmacies_df = pd.read_csv('pharmacies.csv')

# Create a GeoDataFrame from the pharmacies data
pharmacies_gdf = gpd.GeoDataFrame(
    pharmacies_df, 
    geometry=gpd.points_from_xy(pharmacies_df['X'], pharmacies_df['Y']),
    crs='EPSG:4326'
)

# URL for North Carolina county shapefile from the U.S. Census Bureau
nc_counties_url = "https://www2.census.gov/geo/tiger/GENZ2022/shp/cb_2022_us_county_20m.zip"

# Download and extract the shapefile
gdf_counties = gpd.read_file(nc_counties_url)

# Filter North Carolina counties
nc_counties = gdf_counties[gdf_counties['STUSPS'] == 'NC']

# Plot North Carolina counties with the pharmacies
fig, ax = plt.subplots(figsize=(12, 12))
nc_counties.plot(ax=ax, color='white', edgecolor='black')
pharmacies_gdf.plot(ax=ax, color='red', markersize=3)
plt.show()





