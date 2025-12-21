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
    map_center={"lat": df["Lat"].mean(), "lon": df["Lon"].mean()}, 
    autosize=True,
    margin=dict(l=0, r=0, t=0, b=0),
  map_style="open-street-map")   # open-street-map, stamen-terrain, carto-positron "carto-darkmatter", "stamen-terrain" "stamen-toner" "stamen-watercolor"

# Save to HTML
html_file = "index.html"

fig.write_html(
    "index.html",
    include_plotlyjs="cdn",
    full_html=True,
    config={"responsive": True},
    div_id="windfarm-map"
)


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
  <button id="change-style-btn">
    🗺️ Change style
  </button>
  <small class="hint">Shift+S</small>
</div>
"""

view_switcher_html = """
<div id="view-switcher">
  <button id="open-3d">
  🌍 3D Globe
  </button>

  <script>
    document.getElementById("open-3d").addEventListener("click", () => {
      const plotlyDiv =
        document.querySelector(".js-plotly-plot") ||
        document.querySelector(".plotly");

      if (!plotlyDiv || !plotlyDiv.layout || !plotlyDiv.layout.map) {
        // fallback: just open Cesium
        location.href = "cesium.html";
        return;
      }

      const center = plotlyDiv.layout.map.center;
      const zoom = plotlyDiv.layout.map.zoom ?? 5;

      if (!center) {
        location.href = "cesium.html";
        return;
      }

      const url =
        `cesium.html?lat=${center.lat}&lon=${center.lon}&zoom=${zoom}`;

      console.log("Opening Cesium with:", url);
      location.href = url;
    });
    </script>




</div>
"""

style_switcher_js = """
<script>
(function() {
  function ready(fn){
    document.readyState !== 'loading'
      ? fn()
      : document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function() {
    const plotlyDiv = document.querySelector('.js-plotly-plot, .plotly');
    if (!plotlyDiv || !window.Plotly) return;

    const styles = [
      "open-street-map",
      "satellite",
      "carto-voyager",
      "carto-darkmatter"
    ];

    const btn = document.getElementById("change-style-btn");

    let currentIndex = 0;

    // Restore last style
    const saved = localStorage.getItem("map_style_choice");
    if (saved && styles.includes(saved)) {
      currentIndex = styles.indexOf(saved);
      applyStyle(saved);
    }

    btn.addEventListener("click", () => {
      nextStyle();
    });

    // Keyboard shortcut: Shift+S
    document.addEventListener("keydown", e => {
      if (e.key.toLowerCase() === "s" && e.shiftKey) {
        nextStyle();
      }
    });

    function nextStyle() {
      currentIndex = (currentIndex + 1) % styles.length;
      const style = styles[currentIndex];
      localStorage.setItem("map_style_choice", style);
      applyStyle(style);
    }

    async function applyStyle(style) {
      try {
        await Plotly.relayout(plotlyDiv, {
          "map.style": style
        });
        console.log("Map style:", style);
      } catch (err) {
        console.error("Style change failed", err);
      }
    }
  });
})();
</script>
"""

# --- Responsive full-screen CSS ---
custom_css = """
<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

#windfarm-map {
  height: 100dvh;
  width: 100dvw;
  position: relative;
}

@supports not (height: 100dvh) {
  #windfarm-map {
    height: 100vh;
    width: 100vw;
  }
}

/* === Buttons: fully responsive and touch-friendly === */
#view-switcher button,
#style-switcher button {
  font-size: clamp(16px, 2.5vw, 28px);    /* scales with screen width */
  padding: clamp(12px, 2vw, 24px) clamp(16px, 3vw, 28px); /* bigger touch area */
  border-radius: clamp(6px, 1vw, 12px);
  cursor: pointer;
  background: #2c3e50;
  color: white;
  border: none;
}

/* Hint text scales too */
#style-switcher .hint {
  font-size: clamp(11px, 1.5vw, 16px);
  opacity: 0.7;
}

/* Flex layout for buttons */
#view-switcher,
#style-switcher {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: fixed;
  z-index: 10001;
}

/* Bigger hover text on mobile */
#view-switcher button:hover,
#style-switcher button:hover {
  transform: scale(1.05);
  transition: transform 0.15s ease;
}

</style>
"""


# Insert custom CSS into <head>
html_content = html_content.replace("<head>", "<head>\n" + custom_css, 1)

# Insert the dropdown+JS right after <body>
# html_content = html_content.replace("<body>", "<body>\n" + style_selector_html + "\n" + style_switcher_js, 1)
html_content = html_content.replace(
    "<body>",
    "<body>\n"
    + view_switcher_html + "\n"
    + style_selector_html + "\n"
    + style_switcher_js,
    1
)


# (Optional) insert service worker script before </body>
html_content = html_content.replace("</body>", service_worker_script + "\n</body>", 1)

# Save the updated HTML
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)


# # After fig.write_html(...)
# responsive_css = """
# <style>
# @media (max-width: 768px) {
#     .map-container { height: 400px; }
# }
# @media (min-width: 769px) {
#     .map-container { height: 880px; }
# }
# </style>
# """

# with open(html_file, "r", encoding="utf-8") as f:
#     html_content = f.read()

# html_content = html_content.replace("<head>", "<head>\n" + responsive_css, 1)
# html_content = html_content.replace("<body>", "<body>\n<div class='map-container'>", 1)
# html_content = html_content.replace("</body>", "</div>\n</body>", 1)

# with open(html_file, "w", encoding="utf-8") as f:
#     f.write(html_content)

