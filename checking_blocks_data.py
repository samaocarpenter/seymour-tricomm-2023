import geopandas as gpd
import matplotlib.pyplot as plt

# Load the census block data
gdf = gpd.read_file("2010_Census_Block_Groups.zip")

# Extract the total_pop column
total_pop = gdf['total_pop']

# Compute the summary statistics of the total_pop column
summary_stats = total_pop.describe()

print(summary_stats)
print(gdf.head())