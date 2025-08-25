# Read shp file

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from shapely.geometry import Polygon, MultiPolygon
import json

# Load the shapefile
shapefile_path = "data/maritime_boundaries/eez_boundaries_v12.shp"
# load
eez = gpd.read_file(shapefile_path)

# plot in a map the boundaries
eez.plot(figsize=(15, 10))
plt.title("Maritime Boundaries")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.show()

