import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point

# reads in census data
csv_file_path = "NC_Census_2021/table01.csv"
df = pd.read_csv(csv_file_path)

# column names for age brackets of women
women_15_19_idxs = ["B01001_030E", "B01001_031E"]
women_20_24_idxs = ["B01001_032E", "B01001_033E", "B01001_034E"]
women_25_29_idxs = ["B01001_035E"]
women_30_49_idxs = ["B01001_036E", "B01001_037E", "B01001_038E", "B01001_039E"]

# ratios of women who report ever using emergency contraceptives (EC)
ec_px_15_19 = 0.205
ec_px_20_24 = 0.350
ec_px_25_29 = 0.358
ec_px_30_49 = 0.157

# holds the results
df.insert(0, "vulnerability", 0)

# adds up number of women per age group multiplied by ratio of EC usage
for columns, ratio in zip(
    [women_15_19_idxs, women_20_24_idxs, women_25_29_idxs, women_30_49_idxs], 
    [ec_px_15_19, ec_px_20_24, ec_px_25_29, ec_px_30_49]):
        df["vulnerability"] += df[columns].sum(axis=1) * ratio

# EC risk by county, and total number vulnerable
df["vulnerability"] /= (df["B01001_001E"]) + 1

tracts_gdf = gpd.read_file('tl_2021_37_tract.zip')
tracts_gdf = tracts_gdf.to_crs('EPSG:4326')
tracts_gdf["GEOID"] = tracts_gdf["GEOID"].astype(np.int64)

tracts = tracts_gdf.merge(df, on='GEOID', how="outer")

tracts = tracts[(tracts.geometry.centroid.x <= -78.6) | (tracts['B01001_001E'] > 0)]


fig, ax = plt.subplots(figsize=(8,8))

tracts = tracts.to_crs("EPSG:32119")

# plot tracts_gdf
tracts.plot(ax=ax, column='vulnerability', edgecolor='gray', linewidth=0.0, cmap='RdYlBu_r', legend=True)

plt.show()

# save plot
fig.savefig('vulnerability.png', dpi=300, bbox_inches='tight')
