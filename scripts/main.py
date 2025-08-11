import plotly.express as px
import pandas as pd

df = pd.read_csv("data/wind_farms.csv")
df["Diameter"] = df["Diameter"].fillna(50)

fig = px.scatter_map(df, lat="Lat", lon="Lon", 
                    size="Diameter",
                    zoom=3, hover_data=["Country", "Wind Farm", "Model", 
                                        "Diameter", "Rated Power", "Last Update"])
fig.update_traces(
    cluster=dict(enabled=True, maxzoom=7)
    )


# Set map style
fig.update_layout(mapbox_style="open-street-map")

# Save to HTML
fig.write_html("wind_farms_map.html", include_plotlyjs="inline", full_html=True)

fig.show()