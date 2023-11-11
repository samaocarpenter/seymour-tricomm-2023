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

# Import spatial.csv from NC_Census_2021
census_df = pd.read_csv('NC_Census_2021/spatial.csv')


# Create a GeoDataFrame from the spatial data's Latitude and Longitude columns
census_gdf = gpd.GeoDataFrame(
    census_df, 
    geometry=gpd.points_from_xy(census_df['Longitude'], census_df['Latitude']),
    crs='EPSG:4326'
)

# Use 'GeoSeries.to_crs()' to re-project all measures
census_gdf = census_gdf.to_crs('EPSG:32119')
pharmacies_gdf = pharmacies_gdf.to_crs('EPSG:32119')
nc_counties = nc_counties.to_crs('EPSG:32119')

# Calculate distance to nearest pharmacy for each census district
census_gdf['distance_to_pharmacy'] = census_gdf.geometry.apply(lambda x: pharmacies_gdf.distance(x).min())

# Add a binary variable that measures whether the distance is greater or lesser than one mile
census_gdf['within_one_mile'] = census_gdf['distance_to_pharmacy'] <= 1609.34  # 1 mile = 1609.34 meters

# Plot the census data with the new column
fig, ax = plt.subplots(figsize=(12, 12))
nc_counties.plot(ax=ax, color='white', edgecolor='black')
census_gdf.plot(ax=ax, column='within_one_mile', cmap='coolwarm', legend=True, markersize=3)
pharmacies_gdf.plot(ax=ax, color='black', markersize=3, marker='s')
plt.show()