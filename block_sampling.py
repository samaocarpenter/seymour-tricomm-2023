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

print(len(sampled_points))

# Create a new GeoDataFrame with the sampled points
sampled_points_gdf = gpd.GeoDataFrame(sampled_points, crs=blocks.crs)

# Read in the pharmacies data
pharmacies_df = pd.read_csv('pharmacies.csv')

# Create a GeoDataFrame from the pharmacies data
pharmacies_gdf = gpd.GeoDataFrame(
    pharmacies_df,
    geometry=gpd.points_from_xy(pharmacies_df['X'], pharmacies_df['Y']),
    crs='EPSG:4326'
)
pharmacies_gdf = pharmacies_gdf.to_crs('EPSG:32119')

# Calculate accessability metric for each sampled point
for n in ["exponential"]:
    print(f"Calculating accessability metric for n={n}")
    sampled_points_gdf['accessability'] = sampled_points_gdf.geometry.apply(lambda x: sum(np.exp(-pharmacies_gdf.distance(x))))

    # Drop 97.5th percentile of accessability
    sampled_points_gdf = sampled_points_gdf[sampled_points_gdf['accessability'] < np.percentile(sampled_points_gdf['accessability'], 97.5)]

    # Create a histogram of accessibility
    fig, ax = plt.subplots(figsize=(12,12))
    sampled_points_gdf['accessability'].plot.hist(ax=ax, bins=100)
    ax.set(xlabel='Accessibility', ylabel='Frequency', title='Histogram of Accessibility')
    fig.savefig(f"pngs/block_accessability_histogram_n_{n}.png")



    accessibility_by_block = sampled_points_gdf.groupby('block_id')['accessability'].mean()

    # Merge the accessibility data with the block data on geoid10 = block_id
    plot_blocks = blocks.merge(accessibility_by_block, left_on='geoid10', right_on='block_id')

    # Create a plot of the accessability metric
    fig, ax = plt.subplots(figsize=(12,12))
    plot_blocks.plot(column='accessability', ax=ax, legend=True)
    ax.set_axis_off()
    ax.set_title(f"Accessibility Metric for n={n}")

    # Save the plots
    fig.savefig(f"pngs/block_accessability_map_n_{n}.png")

    # Divide the accessibility metric by the population to get the accessability per person
    plot_blocks['accessability_per_person'] = plot_blocks['accessability'] / plot_blocks['total_pop']

    # Create a plot of the accessability per person
    fig, ax = plt.subplots(figsize=(12,12))
    plot_blocks.plot(column='accessability_per_person', ax=ax, legend=True)
    ax.set_axis_off()
    ax.set_title(f"Accessibility per Person for n={n}")

    # Save the plots
    fig.savefig(f"pngs/block_accessability_per_person_map_n_{n}.png")