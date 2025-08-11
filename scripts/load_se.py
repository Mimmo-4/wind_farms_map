'https://data.europa.eu/data/datasets/https-catalog-lansstyrelsen-se-store-2-resource-89?locale=sv'

import geopandas as gpd
import pandas as pd
import numpy as np
import sys
from pyproj import Transformer

sys.path.append("src")
# import utils

# Path to your shapefile (without the extension)
shapefile_path = 'data/Sweden/LST_VKOLLEN_VVERK'

# Read the shapefile
gdf = gpd.read_file(f"{shapefile_path}.shp")
print(len(gdf))
gdf = gdf[gdf["Status"] == "Uppfört"]
print(len(gdf))

df = pd.read_csv("data/wind_farms.csv")
df = df[df["Country"] != "Sweden"]

print(gdf.Status)
print(gdf.columns)

df_se = pd.DataFrame(columns=df.columns)

df_se["Northing"] = gdf["N_Koordina"]
df_se["Easting"] = gdf["E_Koordina"]
df_se["Diameter"] = gdf["Rotordia"]
df_se["Rated Power"] = (gdf["Maxeffekt"].astype(float) * 1000).round(0).astype(str) + " kw"
df_se["Manufacturer"] = gdf["Fabrikat"]
df_se["Model"] = gdf["Modell"]
df_se["Last Update"] = gdf["Sparad"]
df_se["Wind Farm"] = gdf["Proj_omr"]
df_se["Country"] = "Sweden"

# Create a transformer from UTM Zone 32N (EPSG:32632) to WGS84 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:3006", "EPSG:4326", always_xy=True)

# Apply the transformation to your DataFrame
df_se["Lon"], df_se["Lat"] = transformer.transform(df_se["Easting"].values, df_se["Northing"].values)

df_new = pd.concat([df, df_se], ignore_index=True)
df_new.to_csv("data/wind_farms.csv", index=False)
print("Swedish WTs successfully uploaded.")
