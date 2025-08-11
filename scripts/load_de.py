import pandas as pd
from pyproj import Transformer


folder_path = "data/Germany/"
df_de_1 = pd.read_csv(folder_path + "Stromerzeuger_1_to_25000.csv", sep=";")
df_de_2 = pd.read_csv(folder_path + "Stromerzeuger_25001_to_39804.csv", sep=";")
df_de_tot = pd.concat([df_de_1, df_de_2], ignore_index=True)
df_de_tot = df_de_tot[df_de_tot["Betriebs-Status"] == "In Betrieb"]

# Load wind farms database with all countries
df = pd.read_csv("data/wind_farms.csv")
df = df[df["Country"] != "Germany"]

df_de = pd.DataFrame(columns=df.columns)

df_de["Wind Farm"] = df_de_tot["Name des Windparks"]
df_de["Lat"] = df_de_tot["Koordinate: Breitengrad (WGS84)"].str.replace(",", ".")
df_de["Lon"] = df_de_tot["Koordinate: Längengrad (WGS84)"].str.replace(",", ".")

# Create the transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32632", always_xy=True)

# Vectorized transformation
df_de["Easting"], df_de["Northing"] = transformer.transform(
    df_de["Lon"].values,
    df_de["Lat"].values
)

df_de["Model"] = df_de_tot["Typenbezeichnung"]
df_de["Diameter"] = df_de_tot["Rotordurchmesser der Windenergieanlage"].str.replace(",", ".")
df_de["Rated Power"] = df_de_tot["Bruttoleistung der Einheit"] + " kW"
df_de["Manufacturer"] = df_de_tot["Hersteller der Windenergieanlage"]
df_de["Last Update"] = df_de_tot["Letzte Aktualisierung"]
df_de["Country"] = "Germany"

df_new = pd.concat([df, df_de], ignore_index=True)

df_new.to_csv("data/wind_farms.csv", index=False)
print(len(df_new))
print("German WTs successfully uploaded.")
