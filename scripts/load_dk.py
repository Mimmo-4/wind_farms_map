'''
Scripts used to load/update the wind farms in Denmark
'''

import pandas as pd
import sys
sys.path.append("src")
import utils


# df = pd.read_csv("data/wind_farms.csv")

df_dk = pd.read_csv("data/Denmark/wind_farms_dk.csv", sep=";")

df_dk[['Northing', 'Easting']] = df_dk['shape_wkt'].str.extract(r'POINT \(([-\d.]+) ([-\d.]+)\)').astype(float)
df_dk['Lat'], df_dk['Lon'] = utils.get_coordinates_from_utm(df_dk['Northing'], 
                                                            df_dk['Easting'],
                                                            utm_zone_number=32, 
                                                            utm_zone_letter="N")

df_dk.rename(columns={'model': 'Model', 'rotordiam': 'Diameter', 'effekt_kw': 'Rated Power', 'fabrikat': 'Manufacturer', 'ejerlav': 'Wind Farm', 'data_dato': 'Last Update'}, inplace=True)
df_dk["Country"] = "Denmark"
df_dk["Rated Power"] = df_dk["Rated Power"].astype(str) + ' kw'

df_dk = df_dk[["Country", "Wind Farm", "Model", "Rated Power", "Diameter", "Manufacturer", "Last Update", "Northing", "Easting", "Lat", "Lon"]]
df_dk.to_csv("data/wind_farms.csv", index=False)
print("Danish WTs successfully uploaded.")