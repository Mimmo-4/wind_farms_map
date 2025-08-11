import pandas as pd
from pyproj import Transformer


folder_path = "data/Netherlands/"
df_ne_raw = pd.read_csv(folder_path + "Windturbines___vermogen.csv", sep=",")

# df_ne_raw = df_ne_raw[df_ne_raw["Betriebs-Status"] == "In Betrieb"]

# Load wind farms database with all countries
df = pd.read_csv("data/wind_farms.csv")
df = df[df["Country"] != "Netherlands"]

df_ne = pd.DataFrame(columns=df.columns)

# Create a transformer from UTM Zone 32N (EPSG:32632) to WGS84 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)

df_ne["Easting"] = df_ne_raw["x"]
df_ne["Northing"] = df_ne_raw["y"]

# Apply the transformation to your DataFrame
df_ne["Lon"],df_ne["Lat"] = transformer.transform(df_ne["Easting"].values,df_ne["Northing"].values)

df_ne["Wind Farm"] = df_ne_raw["naam"]
df_ne["Model"] = df_ne_raw["wt_type"]
df_ne["Diameter"] = df_ne_raw["diam"]
df_ne["Rated Power"] = df_ne_raw["kw"].astype(str) + " kW"
df_ne["Manufacturer"] = "Unknown"
df_ne["Country"] = df_ne_raw["land"]

df_ne["Country"] = df_ne["Country"].replace({
    "België": "Belgium",
    "Nederland": "Netherlands"
})


df_ne["Last Update"] = "Unknown"

df_new = pd.concat([df, df_ne], ignore_index=True)

df_new.to_csv("data/wind_farms.csv", index=False)

print("Dutch WTs successfully uploaded.")
