import pandas as pd
import plotly.graph_objects as go

# Load your dataset
df = pd.read_csv("data/wind_farms.csv")
df["Diameter"] = df["Diameter"].fillna(50)

# Create the map trace
trace = go.Scattermapbox(
    lat=df["Lat"],
    lon=df["Lon"],
    mode="markers",
    marker=go.scattermapbox.Marker(
        size=df["Diameter"],
        color="blue",
        opacity=0.6
    ),
    text=df["Wind Farm"],
    customdata=df[["Country", "Wind Farm", "Model", "Diameter", "Rated Power", "Last Update"]],
    hovertemplate=(
        "<b>%{customdata[1]}</b><br>" +
        "Country: %{customdata[0]}<br>" +
        "Model: %{customdata[2]}<br>" +
        "Diameter: %{customdata[3]}<br>" +
        "Rated Power: %{customdata[4]}<br>" +
        "Last Update: %{customdata[5]}<br><extra></extra>"
    )
)

# Create the figure
fig = go.Figure(data=[trace])

# Initial layout
fig.update_layout(
    mapbox=dict(
        style="open-street-map",
        zoom=5,
        center=dict(lat=df["Lat"].mean(), lon=df["Lon"].mean())
    ),
    margin={"r":0,"t":0,"l":0,"b":0},
    updatemenus=[
        dict(
            buttons=[
                dict(label="OpenStreetMap",
                    method="relayout",
                    args=[{"mapbox.style": "open-street-map"}]),
                dict(label="Carto Positron",
                    method="relayout",
                    args=[{"mapbox.style": "carto-positron"}]),
            ],
            direction="down",
            showactive=True,
            x=0.05,
            xanchor="left",
            y=1.05,
            yanchor="top"
        )
    ]
)

# Save to HTML
html_file = "index.html"
fig.write_html(html_file, include_plotlyjs="inline", full_html=True)

# Inject manifest block
manifest_block = """
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#2c3e50">
"""

with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

html_content = html_content.replace("<head>", "<head>\n" + manifest_block, 1)

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

# Show the map
fig.show()


# -----------------------


# Save to HTML
html_file = "index.html"
fig.write_html(html_file, include_plotlyjs="inline", full_html=True)

fig.show()

# Modify html head
manifest_block = """
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#2c3e50">
"""

with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# Insert header block for manifest and theme color
html_content = html_content.replace("<head>", "<head>\n" + manifest_block, 1)

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)
