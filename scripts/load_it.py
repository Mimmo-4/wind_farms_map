'atlanti RSE'

import geopandas as gpd
import pandas as pd
import numpy as np
import sys
from pyproj import Transformer

sys.path.append("src")
import utils

# Path to your shapefile (without the extension)
shapefile_path = 'data/Italy/d__temp_aerogeneratori_2019/aerogeneratori_2019'

# Read the shapefile
gdf = gpd.read_file(f"{shapefile_path}.shp")

df = pd.read_csv("data/wind_farms.csv")
df = df[df["Country"] != "Italy"]

df_it = pd.DataFrame(columns=df.columns)

df_it["Northing"] = gdf["LATITUDINE"]
df_it["Easting"] = gdf["LONGITUDIN"]
df_it["Rated Power"] = gdf["CLASSE_POT"]

# Create a transformer from UTM Zone 32N (EPSG:32632) to WGS84 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

# Apply the transformation to your DataFrame
df_it["Lon"], df_it["Lat"] = transformer.transform(df_it["Easting"].values, df_it["Northing"].values)

df_it["Country"] = "Italy"
df_it["Model"] = "Not available"
df_it["Diameter"] = np.nan
df_it["Wind Farm"] = "Not available"

df_new = pd.concat([df, df_it], ignore_index=True)
df_new.to_csv("data/wind_farms.csv", index=False)
print("Italian WTs successfully uploaded.")
