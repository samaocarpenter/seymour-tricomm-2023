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

# Import total county population
county_pop = pd.read_csv('NC_Census_2021/table01.csv')

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

# Import county urban/rural classification as a DataFrame
nc_urban = pd.read_csv('nc_counties.csv')

# Merge the urban/rural classification with the county file
nc_counties = nc_counties.merge(nc_urban, on='NAME')


# Calculate distance to nearest pharmacy for each census district
census_gdf['distance_to_pharmacy'] = census_gdf.geometry.apply(lambda x: pharmacies_gdf.distance(x).min())

# Perform a spatial join between census_gdf and nc_counties
census_counties = gpd.sjoin(census_gdf, nc_counties, op='within')

# Create a function to determine pharmacy desert
def is_pharmacy_desert(row):
    if row['URBAN'] == 2:
        return row['distance_to_pharmacy'] > 1609.34  # 1 mile = 1609.34 meters
    elif row['URBAN'] == 1:
        return row['distance_to_pharmacy'] > 3218.69  # 2 miles = 3218.69 meters
    else:
        return row['distance_to_pharmacy'] > 8046.72  # 5 miles = 8046.72 meters

# Add a column to census_counties to indicate whether it is a pharmacy desert
census_counties['pharmacy_desert'] = census_counties.apply(is_pharmacy_desert, axis=1)

# Plot the census data with the new column
fig, ax = plt.subplots(figsize=(12, 12))
nc_counties.plot(ax=ax, column='URBAN', cmap='RdYlGn_r', alpha=0.5, legend=False, edgecolor='black')
census_counties.plot(ax=ax, column='pharmacy_desert', cmap='coolwarm', legend=True, markersize=3, legend_kwds={'labels': {True: 'Pharmacy desert', False: 'Not a pharmacy desert'}})
#pharmacies_gdf.plot(ax=ax, color='black', markersize=3)
plt.show()