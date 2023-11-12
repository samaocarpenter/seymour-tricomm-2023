import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point

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

'''
Haussdorf distance process
1. Repeat loop n times to accrue a dataset
2. For each iteration, calculate the point cloud distance between every other point cloud
3. Calculate summary statistics for Haussdorf distances
'''
iteration_holder = []
for i in range(0, 10):
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

    iteration_holder.append(sampled_points_gdf)

# Create a list of all the Haussdorf distances
haussdorf_distances = []
for i in range(0, len(iteration_holder)):
    for j in range(0, len(iteration_holder)):
        if i != j:
            haussdorf_distances.append(iteration_holder[i].geometry.hausdorff_distance(iteration_holder[j].geometry, densify = 0.00001))

# Report haussdorf summary statistics
print('Mean: ' + str(np.mean(haussdorf_distances)))
print('Median: ' + str(np.median(haussdorf_distances)))
print('Min: ' + str(np.min(haussdorf_distances)))
print('Max: ' + str(np.max(haussdorf_distances)))
print('Standard Deviation: ' + str(np.std(haussdorf_distances)))
