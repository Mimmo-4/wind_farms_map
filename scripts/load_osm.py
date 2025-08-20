import json
from collections import Counter
import pprint

# Load the GeoJSON file
with open("data/OSM/export.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Extract features
features = geojson_data.get("features", [])

# Print number of features
print(f"Total number of features: {len(features)}")

# Print geometry types
geometry_types = Counter()
for feature in features:
    geom = feature.get("geometry", {})
    geometry_types[geom.get("type", "Unknown")] += 1

print("\nGeometry types:")
for geom_type, count in geometry_types.items():
    print(f"- {geom_type}: {count}")

# Collect all unique property keys
property_keys = set()
for feature in features:
    props = feature.get("properties", {})
    property_keys.update(props.keys())

print("\nUnique property keys (columns):")
for key in sorted(property_keys):
    print(f"- {key}")

# Optional: Preview the first feature
# print("\nFirst feature preview:")
# pprint.pprint(features[0], depth=3)

# Filter properties of interest from a list
property_of_interest = ["name", "height:hub", "manufacturer", "model", "operator", "rotor:diameter", "start_date"]

filtered_features = []
for feature in features:
    props = feature.get("properties", {})
    filtered_props = {key: props[key] for key in property_of_interest if key in props}
    if filtered_props:
        filtered_feature = feature.copy()
        filtered_feature["properties"] = filtered_props
        filtered_features.append(filtered_feature)

# Create pandas dataframe with filtered_features
import pandas as pd
df = pd.json_normalize(filtered_features)
# Print the dataframe
print("\nFiltered DataFrame:")
print(df.head(20))
print(df.info())

# Keep only the rows with geometry.type "Point"
df = df[df["geometry.type"] == "Point"]
# reset index
df.reset_index(drop=True, inplace=True)

# Separate the coordinates into latitude and longitude as other columns
df["Lon"] = df["geometry.coordinates"].apply(lambda x: x[0] if isinstance(x, list) else None)
df["Lat"] = df["geometry.coordinates"].apply(lambda x: x[1] if isinstance(x, list) else None)

# Rename columns
df.rename(columns={
    "properties.rotor:diameter": "Diameter",
    "properties.height:hub": "Hub Height",
    "properties.manufacturer": "Manufacturer",
    "properties.operator": "Operator",
    "properties.power_rating": "rating",
    "properties.model": "Model",
}, inplace=True)

# Drop columns geometry
df.drop(columns=["geometry.coordinates", "geometry.type"], inplace=True)

# convert diameter columns type to float or NaN
df["Diameter"] = pd.to_numeric(df["Diameter"], errors='coerce')

print(df.columns)

# Save as csv file named wind_farms
df.to_csv("data/wind_farms.csv", index=False)