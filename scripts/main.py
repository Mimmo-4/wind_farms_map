import plotly.express as px
import pandas as pd

df = pd.read_csv("data/wind_farms.csv")
df["Diameter"] = df["Diameter"].fillna(50)

fig = px.scatter_map(df, lat="Lat", lon="Lon", 
                    size="Diameter",
                    zoom=5, hover_data=["Diameter", "Hub Height", "Total Height", "Manufacturer", "Model", "Operator", "Rated Power", "Start Date"],   # country, wind farm, last update
                    )

fig.update_traces(
    cluster=dict(enabled=True, maxzoom=7)
    )


# Set map style
fig.update_layout(
    # map_center={"lat": df["Lat"].mean(), "lon": df["Lon"].mean()}, 
    map_style="open-street-map")   # open-street-map, stamen-terrain, carto-positron "carto-darkmatter", "stamen-terrain" "stamen-toner" "stamen-watercolor"

# Save to HTML
html_file = "index.html"
fig.write_html(html_file, include_plotlyjs="inline", full_html=True)

# fig.show()

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

# splash_css = """
# <style>
#     #splash-screen {
#         position: fixed;
#         top: 0; left: 0;
#         width: 100%; height: 100%;
#         background-color: #1287cd;
#         display: flex;
#         flex-direction: column;
#         justify-content: center;
#         align-items: center;
#         z-index: 9999;
#     }
#     #splash-screen img {
#         width: 2700;
#         height: 2700px;
#     }
#     #splash-screen h1 {
#         color: white;
#         font-size: 48px;
#         margin-top: 20px;
#     }
# </style>
# """

# splash_html = """
# <div id="splash-screen">
#     <img src="icon-512.png" alt="Logo">
#     <h1>Wind Farms Map</h1>
# </div>
# <script>
#     setTimeout(() => {
#         document.getElementById('splash-screen').style.display = 'none';
#     }, 4000);
# </script>
# """

# Insert splash CSS into <head>
# html_content = html_content.replace("<head>", "<head>\n" + splash_css, 1)

# Insert splash HTML into <body>
# html_content = html_content.replace("<body>", "<body>\n" + splash_html, 1)



# --- Basemap dropdown + Update Now button (REAL HTML + JS) ---
style_selector_html = """
<div id="style-switcher">
  <label for="map-style">Map style:</label>
  <select id="map-style">
    <option value="open-street-map">OpenStreetMap</option>
    <option value="satellite">Satellite</option>
    <option value="carto-voyager">Carto Voyager</option>
    <option value="carto-darkmatter">Carto Darkmatter</option>
  </select>
  <button id="apply-style">Change style</button>
  <small>Press <b>Shift+S</b> to change style</small>
</div>
"""

style_switcher_js = """
<script>
(function() {
  // Run after DOM is ready
  function ready(fn){ document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn); }

  ready(function() {
    // Find the Plotly figure div
    const plotlyDiv = document.querySelector('.js-plotly-plot, .plotly');
    if (!plotlyDiv || !window.Plotly) {
      console.warn('Plotly div not found or Plotly is not loaded.');
      return;
    }

    const select = document.getElementById('map-style');
    const applyBtn = document.getElementById('apply-style');
    const styles = Array.from(select.options).map(opt => opt.value);

    // Restore last selection
    const saved = localStorage.getItem('map_style_choice');
    if (saved && styles.includes(saved)) {
      select.value = saved;
      applyStyle(saved);
    }

    // Dropdown change
    select.addEventListener('change', e => {
      const style = e.target.value;
      localStorage.setItem('map_style_choice', style);
      applyStyle(style);
    });

    // "Update now" button
    applyBtn.addEventListener('click', () => applyStyle(select.value));

    // Keyboard: Shift+S cycles styles
    document.addEventListener('keydown', e => {
      if (e.key.toLowerCase() === 's' && e.shiftKey) {
        const idx = styles.indexOf(select.value);
        const next = styles[(idx + 1) % styles.length];
        select.value = next;
        localStorage.setItem('map_style_choice', next);
        applyStyle(next);
      }
    });

    async function applyStyle(styleValue) {
      try {
        // MapLibre traces use layout.map.style
        await Plotly.relayout(plotlyDiv, { 'map.style': styleValue });
        console.log('Applied map style:', styleValue);
      } catch(err) {
        console.error('Failed to apply map style', err);
      }
    }
  });
})();
</script>
"""

custom_css = """
<style>
    .plotly .modebar-btn,
    .plotly .dropdown {
        font-size: 200% !important;
    }
    .hoverlayer .hovertext {
        font-size: 200% !important;
        padding: 20px !important;
    }
</style>
"""

# Insert custom CSS into <head>
html_content = html_content.replace("<head>", "<head>\n" + custom_css, 1)

# Insert the dropdown+JS right after <body>
html_content = html_content.replace("<body>", "<body>\n" + style_selector_html + "\n" + style_switcher_js, 1)

# (Optional) insert service worker script before </body>
html_content = html_content.replace("</body>", service_worker_script + "\n</body>", 1)

# Save the updated HTML
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)


# After fig.write_html(...)
responsive_css = """
<style>
@media (max-width: 768px) {
    .map-container { height: 400px; }
}
@media (min-width: 769px) {
    .map-container { height: 800px; }
}
</style>
"""

with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

html_content = html_content.replace("<head>", "<head>\n" + responsive_css, 1)
html_content = html_content.replace("<body>", "<body>\n<div class='map-container'>", 1)
html_content = html_content.replace("</body>", "</div>\n</body>", 1)

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

