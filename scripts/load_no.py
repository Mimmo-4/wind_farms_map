'https://data.europa.eu/data/datasets/https-catalog-lansstyrelsen-se-store-2-resource-89?locale=sv'

import geopandas as gpd
import pandas as pd
import numpy as np
import sys
from pyproj import Transformer

sys.path.append("src")
# import utils

# Path to your shapefile (without the extension)
shapefile_path = 'data/Norway/Vindkraft_Vindturbin'

# Read the shapefile
gdf = gpd.read_file(f"{shapefile_path}.shp")
# print(len(gdf))
# gdf = gdf[gdf["Status"] == "Uppfört"]
# print(len(gdf))

df = pd.read_csv("data/wind_farms.csv")
df = df[df["Country"] != "Norway"]

print(gdf.columns)

df_no = pd.DataFrame(columns=df.columns)

df_no[['Lon', 'Lat']] = gdf['geometry'].astype(str).str.extract(r'POINT Z \(([-\d.]+) ([-\d.]+) [-\d.]+\)').astype(float)

# Create the transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:25833", always_xy=True)

df_no["Easting"], df_no["Northing"] = transformer.transform(
    df_no["Lon"].values,
    df_no["Lat"].values
)
df_no["Wind Farm"] = gdf["sakTittel"]

df_no["Diameter"] = np.nan
df_no["Rated Power"] = "Unknown"
df_no["Manufacturer"] = "Unknown"
df_no["Model"] = "Unknown"
df_no["Last Update"] = gdf["uttakDato"]
df_no["Country"] = "Norway"

df_new = pd.concat([df, df_no], ignore_index=True)
df_new.to_csv("data/wind_farms.csv", index=False)
print("Norwegian WTs successfully uploaded.")
