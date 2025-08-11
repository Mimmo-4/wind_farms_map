import folium
from folium.plugins import MarkerCluster
import pandas as pd

df = pd.read_csv("data/wind_farms.csv")
df["Diameter"] = df["Diameter"].fillna(50)

# Create map
m = folium.Map(location=[54, 10], zoom_start=5)

# Add clustered markers with custom icons
marker_cluster = MarkerCluster().add_to(m)
for _, row in df.iterrows():
    folium.Marker(
        location=[row["Lat"], row["Lon"]],
        popup=f"{row['Wind Farm']} ({row['Model']})",
        icon=folium.Icon(color="green", icon="leaf", prefix="fa")  # Font Awesome icon
    ).add_to(marker_cluster)

# Save to HTML
m.save("custom_wind_farm_map.html")
