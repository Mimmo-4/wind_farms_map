import plotly.express as px
import pandas as pd

df = pd.read_csv("data/wind_farms.csv")
df["Diameter"] = df["Diameter"].fillna(50)

fig = px.scatter_map(df, lat="Lat", lon="Lon", 
                    size="Diameter",
                    zoom=5, hover_data=["Diameter", "Hub Height", "Manufacturer", "Model", "Operator"])   # country, wind farm, last update

fig.update_traces(
    cluster=dict(enabled=True, maxzoom=7)
    )


# Set map style
fig.update_layout(mapbox_style="open-street-map")

# Save to HTML
html_file = "index.html"
fig.write_html(html_file, include_plotlyjs="inline", full_html=True)

fig.show()

# Modify html head
manifest_block = """
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#2c3e50">
"""

# Service worker registration for <body>
service_worker_script = """
<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('service-worker.js')
            .then(reg => console.log('Service Worker registered:', reg))
            .catch(err => console.error('Service Worker registration failed:', err));
    }
</script>
"""

# Modify the HTML
with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# Insert manifest block into <head>
html_content = html_content.replace("<head>", "<head>\n" + manifest_block, 1)

# Custom CSS for hover box styling
custom_css = """
<style>
    .hoverlayer .hovertext {
        font-size: 36px !important;
        padding: 20px !important;
    }
</style>
"""

# Insert custom CSS into <head>
html_content = html_content.replace("<head>", "<head>\n" + custom_css, 1)

# Insert service worker script before </body>
html_content = html_content.replace("</body>", service_worker_script + "\n</body>", 1)

# Save the modified HTML
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)
