import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point

# set numpy seed to 0
np.random.seed(0)

tracts = gpd.read_file('tl_2019_37_tract.zip')
tracts = tracts.to_crs('EPSG:4326')
populations = pd.read_csv('NC_Census_2021/table02.csv')

# Only select first two columns from populations
populations = populations.iloc[:, :2]

# Merge populations into tracts by GEOID, convert to int
tracts['GEOID'] = tracts['GEOID'].astype(int)
populations['GEOID'] = populations['GEOID'].astype(int)

tracts = tracts.merge(populations, on='GEOID', how='left')

# Rename the column to 'population'
tracts.rename(columns={'B18101_001E': 'population'}, inplace=True)

# Sample n points inside each tract
sampled_points = []
for index, tract in tracts.iterrows():
    points = []
    minx, miny, maxx, maxy = tract.geometry.bounds

    # define n as a percentage of the population, if no population data, use 10
    if tract['population'] > 0:
        n = int(tract['population'] * 0.01)
    else:
        n = 10
    while len(points) < n:
        random_point = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if random_point.within(tract.geometry):
            points.append(random_point)
    for point in points:
        sampled_points.append({'geometry': point, 'tract_id': tract['GEOID']})


# Create a new GeoDataFrame with the sampled points
sampled_points_gdf = gpd.GeoDataFrame(sampled_points, crs=tracts.crs)

# Save the sampled points to a shapefile
#sampled_points_gdf.to_file('sampled_points.shp')

# Read in the pharmacies data
pharmacies_df = pd.read_csv('pharmacies.csv')

# Create a GeoDataFrame from the pharmacies data
pharmacies_gdf = gpd.GeoDataFrame(
    pharmacies_df, 
    geometry=gpd.points_from_xy(pharmacies_df['X'], pharmacies_df['Y']),
    crs='EPSG:4326'
)
pharmacies_gdf = pharmacies_gdf.to_crs('EPSG:32119')
tracts = tracts.to_crs('EPSG:32119')
sampled_points_gdf = sampled_points_gdf.to_crs('EPSG:32119')



# Calculate accessability metric for each sampled point
for n in [0.85,0.95,1.15,1.25,1.35,1.45]:
    print(f"Calculating accessability metric for n={n}")
    sampled_points_gdf['accessability'] = sampled_points_gdf.geometry.apply(lambda x: sum(1/pharmacies_gdf.distance(x)**n))

    # Plot histogram of accessability metric
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(24, 12))
    axs[0].hist(sampled_points_gdf['accessability'], bins=100)
    axs[0].set_title(f"Accessibility Metric Histogram (n={n})")
    axs[0].set_xlabel("Accessibility Metric")
    axs[0].set_ylabel("Frequency")

    # Remove points with accessability metric quantile > 0.95
    sampled_points_gdf = sampled_points_gdf[sampled_points_gdf['accessability'] < sampled_points_gdf['accessability'].quantile(0.95)]

    # Plot the points on top of the tracts with accessability as the color
    tracts.plot(ax=axs[1], color='white', edgecolor='black')
    sampled_points_gdf.plot(ax=axs[1], column='accessability', cmap='coolwarm', legend = True, markersize=1)
    pharmacies_gdf.plot(ax=axs[1], color='black', markersize=1)
    axs[1].set_title(f"Accessibility Metric Map (n={n})")
    axs[1].set_xlabel("Longitude")
    axs[1].set_ylabel("Latitude")

    # Save the plots
    fig.savefig(f"pngs/accessability_metric_n_{n}.png")

# Running the calculations and then saving them to a csv for analysis
n = 1.3
sampled_points_gdf['accessability'] = sampled_points_gdf.geometry.apply(lambda x: sum(1/pharmacies_gdf.distance(x)**n))

sampled_points_gdf.to_csv('accessability.csv')

