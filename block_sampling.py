import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point


# set numpy seed to 0
np.random.seed(0)

# Read in census block shape file
gdf_block = gpd.read_file('2010_Census_Block_Groups.zip')
# Change the projection
gdf_block = gdf_block.to_crs('EPSG:32119')

# Keep shapes where the total_pop > 0 OR are left of the -78.6 longitude
blocks = gdf_block[(gdf_block['total_pop'] > 0) | (gdf_block.geometry.centroid.x < -78.6)]

# Import county borders
counties = gpd.read_file('county_boundary.zip')
# Change the projection
counties = counties.to_crs('EPSG:32119')

print(counties.head())
print(counties.columns)

# Calculate population density of every block
blocks['pop_density'] = (blocks['total_pop'] / blocks['st_areasha']) * 0.00386102

# Sample n points inside each block
sampled_points = []
for index, block in blocks.iterrows():
    points = []
    minx, miny, maxx, maxy = block.geometry.bounds

    # define n as 1% of the population, rounded up to the nearest integer
    n = int(block['total_pop'] * 0.01)
    while len(points) < n:
        random_point = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if random_point.within(block.geometry):
            points.append(random_point)
    for point in points:
        sampled_points.append({'geometry': point, 'block_id': block['geoid10']})

# Create a new GeoDataFrame with the sampled points
sampled_points_gdf = gpd.GeoDataFrame(sampled_points, crs=blocks.crs)

'''
# Create a plot of the sampled points on county borders
fig, ax = plt.subplots(figsize=(12,12))
# Plot the Durham County points in blue
sampled_points_gdf[sampled_points_gdf.geometry.within(counties[counties['County'] == 'Durham'].iloc[0].geometry)].plot(ax=ax, color='blue', markersize=1)

# Add census block borders to the plot with a thinner black color
blocks.plot(ax=ax, color='none', edgecolor='black', linewidth=0.5)

# Set the borders of counties.plot to be a thick black
counties.plot(ax=ax, color='none', edgecolor='black', linewidth=2)
# Show the plot
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Sampled Points in Durham County Borders')
plt.show()
'''

# Read in the pharmacies data
pharmacies_df = pd.read_csv('pharmacies.csv')

# Create a GeoDataFrame from the pharmacies data
pharmacies_gdf = gpd.GeoDataFrame(
    pharmacies_df,
    geometry=gpd.points_from_xy(pharmacies_df['X'], pharmacies_df['Y']),
    crs='EPSG:4326'
)
pharmacies_gdf = pharmacies_gdf.to_crs('EPSG:32119')

def distance_taper(distance, n):
    return (-2 / (1 + np.exp(-(distance - n))))+ 2

# Calculate accessibility metric for each sampled point
for n in [0.9]:
    print(f"Calculating accessibility metric for n={n}")
    sampled_points_gdf['accessibility'] = sampled_points_gdf.geometry.apply(lambda x: sum(1/pharmacies_gdf.distance(x)**n))

    # Drop 99th percentile of accessibility
    sampled_points_gdf = sampled_points_gdf[sampled_points_gdf['accessibility'] < np.percentile(sampled_points_gdf['accessibility'], 99)]

    # Create a histogram of accessibility
    fig, ax = plt.subplots(figsize=(8,8))
    sampled_points_gdf['accessibility'].plot.hist(ax=ax, bins=100)
    ax.set(xlabel='Accessibility', ylabel='Frequency', title='Histogram of Accessibility')
    fig.savefig(f"pngs/block_accessibility_histogram_n_{n}.png")

    #accessibility_by_block = sampled_points_gdf.groupby('block_id')['accessibility'].mean()
    print(sampled_points_gdf.head())
    print(counties.head())

    # Perform a spatial join to assign each point to a county
    sampled_points_counties = gpd.sjoin(sampled_points_gdf, counties, op='within')
    print(sampled_points_counties.head())
    # Calculate the mean accessibility for each county
    accessibility_by_county = sampled_points_counties.groupby('County')['accessibility'].mean()

    print(accessibility_by_county.head())

    # Merge the accessibility data with the county data on the county name or county FIPS code
    county_data = counties.merge(accessibility_by_county, left_on='County', right_index=True)

    # Create a plot of the accessibility metric
    fig, ax = plt.subplots(figsize=(12,12))
    county_data.plot(column='accessibility', ax=ax, legend=True)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title(f"Accessibility Metric for n={n}")
    #plt.show()
    # Save the plots
    fig.savefig(f"pngs/block_accessibility_map_n_{n}.png")

    # Perform a spatial join to assign each census block to a county
    census_blocks_counties = gpd.sjoin(blocks, counties, op='within')

    print(census_blocks_counties.head())

    # Group the census blocks by county and sum the population figures to get the total population for each county
    total_pop_by_county = census_blocks_counties.groupby('County')['total_pop'].sum()

    print(total_pop_by_county.head())

    # Join total_pop_by_county to the county_data GeoDataFrame
    county_data = county_data.merge(total_pop_by_county, left_on='County', right_index=True)

    # Calculate the population density for each county
    county_data['pop_density'] = county_data['total_pop'] / county_data['Shape__Are']

    print(county_data.head())



    # Create a plot of the accessibility metric vs. population density
    fig, axs = plt.subplots(2, 2, figsize=(12, 12))

    # Plot 1: log accessibility vs. log population density
    axs[0, 0].scatter(np.log(county_data['pop_density']), np.log(county_data['accessibility']))
    axs[0, 0].set_xlabel('Log Population Density')
    axs[0, 0].set_ylabel('Log Accessibility')
    axs[0, 0].set_title(f"Accessibility vs. Population Density for n={n}")

    # Plot 2: accessibility vs. population density
    axs[0, 1].scatter(county_data['pop_density'], county_data['accessibility'])
    axs[0, 1].set_xlabel('Population Density')
    axs[0, 1].set_ylabel('Accessibility')
    axs[0, 1].set_title(f"Accessibility vs. Population Density for n={n}")

    # Plot 3: log accessibility vs. population density
    axs[1, 0].scatter(county_data['pop_density'], np.log(county_data['accessibility']))
    axs[1, 0].set_xlabel('Population Density')
    axs[1, 0].set_ylabel('Log Accessibility')
    axs[1, 0].set_title(f"Accessibility vs. Population Density for n={n}")

    # Plot 4: accessibility vs. log population density
    axs[1, 1].scatter(np.log(county_data['pop_density']), county_data['accessibility'])
    axs[1, 1].set_xlabel('Log Population Density')
    axs[1, 1].set_ylabel('Accessibility')
    axs[1, 1].set_title(f"Accessibility vs. Population Density for n={n}")

 

    # print out correlation coefficients
    print(f"Correlation coefficient for log accessibility vs. log population density for n={n}: {np.corrcoef(np.log(county_data['pop_density']), np.log(county_data['accessibility']))[0,1]}")
    print(f"Correlation coefficient for accessibility vs. population density for n={n}: {np.corrcoef(county_data['pop_density'], county_data['accessibility'])[0,1]}")
    print(f"Correlation coefficient for log accessibility vs. population density for n={n}: {np.corrcoef(county_data['pop_density'], np.log(county_data['accessibility']))[0,1]}")
    print(f"Correlation coefficient for accessibility vs. log population density for n={n}: {np.corrcoef(np.log(county_data['pop_density']), county_data['accessibility'])[0,1]}")

    plt.show()