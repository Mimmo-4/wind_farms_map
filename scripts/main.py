import re
import plotly.express as px
import pandas as pd

df = pd.read_csv("data/wind_farms.csv", low_memory=False)
df["Diameter"] = df["Diameter"].fillna(50)


def parse_power_kw(raw):
    """Parse a raw power string/number to kW. Returns NaN if unparseable."""
    if pd.isna(raw):
        return float("nan")
    if isinstance(raw, (int, float)):
        n = float(raw)
        # Bare numbers > 50 000 were stored as kW but are actually MW values
        # (e.g. 2 850 000 → 2 850 kW = 2.85 MW)
        if n > 50_000:
            n /= 1000
        return n if n > 0 else float("nan")
    s = str(raw).strip().replace(",", ".")
    m = re.match(r"^([0-9.]+)\s*(GW|MW|kW|W)$", s, re.IGNORECASE)
    if m:
        val, unit = float(m.group(1)), m.group(2).lower()
        if unit == "gw":
            return val * 1_000_000
        if unit == "mw":
            kw = val * 1000
            # Values labeled "MW" exceeding a realistic single-turbine max are
            # almost certainly kW values mislabeled as MW (data quality issue).
            # Largest real turbine today is ~22 MW; 30 MW gives safe headroom.
            return kw / 1000 if kw > 30_000 else kw
        if unit == "kw":
            # Same mislabeling guard: kW values > 30 000 are almost certainly
            # watt values mislabeled as kW (e.g. 5 500 000 kW → 5 500 kW = 5.5 MW)
            return val if val <= 30_000 else val / 1000
        if unit == "w":
            return val / 1000
    m2 = re.match(r"^([0-9.]+)$", s)
    if m2:
        n = float(m2.group(1))
        if n > 50_000:
            n /= 1000
        return n if n > 0 else float("nan")
    return float("nan")


df["Rated Power (kW)"] = df["Rated Power"].apply(parse_power_kw)
df["Rated Power (MW)"] = (df["Rated Power (kW)"] / 1000).round(3)

# Discrete power categories — identical thresholds as the 3D globe
CAT_ORDER = ["< 0.5 MW", "0.5 – 5 MW", "5 – 10 MW", "10 – 15 MW", "> 15 MW", "Unknown"]
CAT_COLORS = {
    "< 0.5 MW":   "#3366ff",
    "0.5 – 5 MW": "#00ccff",
    "5 – 10 MW":  "#33e05a",
    "10 – 15 MW": "#ffd000",
    "> 15 MW":    "#ff4b1a",
    "Unknown":    "#888888",
}


def power_cat(kw):
    if pd.isna(kw):   return "Unknown"
    if kw < 500:      return "< 0.5 MW"
    if kw < 5000:     return "0.5 – 5 MW"
    if kw < 10000:    return "5 – 10 MW"
    if kw < 15000:    return "10 – 15 MW"
    return "> 15 MW"


df["Power Category"] = df["Rated Power (kW)"].apply(power_cat)

fig = px.scatter_map(
    df, lat="Lat", lon="Lon",
    size="Diameter",
    color="Power Category",
    color_discrete_map=CAT_COLORS,
    category_orders={"Power Category": CAT_ORDER},
    zoom=5,
    hover_name="properties.name",
    hover_data={
        "Diameter":          True,
        "Hub Height":        True,
        "Total Height":      True,
        "Manufacturer":      True,
        "Model":             True,
        "Operator":          True,
        "Rated Power (MW)":  True,
        "Rated Power":       False,
        "Rated Power (kW)":  False,
        "Power Category":    False,
        "Start Date":        True,
        "Lat":               False,
        "Lon":               False,
    },
)

fig.update_traces(
    cluster=dict(enabled=True, maxzoom=7),
    hoverlabel=dict(font_size=15, namelength=-1),
)

fig.update_layout(
    map_center={"lat": df["Lat"].mean(), "lon": df["Lon"].mean()},
    autosize=True,
    margin=dict(l=0, r=0, t=0, b=0),
    map_style="open-street-map",
    showlegend=False,
)

# Save to HTML
html_file = "index.html"

fig.write_html(
    "index.html",
    include_plotlyjs="cdn",
    full_html=True,
    config={"responsive": True},
    div_id="windfarm-map"
)


# Modify html head
manifest_block = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#2c3e50">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
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

# --- Custom legend (replaces Plotly's internal legend which disappears on zoom) ---
legend_2d_html = """
<div id="legend-2d">
  <h4>Rated Power</h4>
  <div class="leg-row"><div class="leg-dot" style="background:#3366ff"></div><span>&lt; 0.5 MW</span></div>
  <div class="leg-row"><div class="leg-dot" style="background:#00ccff"></div><span>0.5 &ndash; 5 MW</span></div>
  <div class="leg-row"><div class="leg-dot" style="background:#33e05a"></div><span>5 &ndash; 10 MW</span></div>
  <div class="leg-row"><div class="leg-dot" style="background:#ffd000"></div><span>10 &ndash; 15 MW</span></div>
  <div class="leg-row"><div class="leg-dot" style="background:#ff4b1a"></div><span>&gt; 15 MW</span></div>
  <div class="leg-row"><div class="leg-dot" style="background:#888"></div><span>Unknown</span></div>
</div>
"""

# --- Basemap dropdown + Update Now button (REAL HTML + JS) ---
style_selector_html = """
<div id="style-switcher">
  <button id="change-style-btn">🗺️ Change style</button>
  <small class="hint">Shift+S</small>
</div>

<div id="stats-bar-2d">🌬️ 246,229 turbines worldwide</div>
"""

view_switcher_html = """
<div id="view-switcher">
  <button id="open-3d">🌍 3D Globe</button>
</div>
"""

style_switcher_js = """
<script>
(function () {
  function ready(fn) {
    document.readyState !== 'loading'
      ? fn()
      : document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    const plotlyDiv = document.querySelector('.js-plotly-plot, .plotly');
    if (!plotlyDiv || !window.Plotly) return;

    // ── Style switcher ────────────────────────────────────────────────────────
    const styles = ['open-street-map', 'satellite', 'carto-voyager', 'carto-darkmatter'];
    const styleBtn = document.getElementById('change-style-btn');
    let currentIndex = 0;

    const saved = localStorage.getItem('map_style_choice');
    if (saved && styles.includes(saved)) {
      currentIndex = styles.indexOf(saved);
      applyStyle(saved);
    }

    styleBtn.addEventListener('click', nextStyle);
    document.addEventListener('keydown', e => {
      if (e.key.toLowerCase() === 's' && e.shiftKey) nextStyle();
    });

    function nextStyle() {
      currentIndex = (currentIndex + 1) % styles.length;
      const style = styles[currentIndex];
      localStorage.setItem('map_style_choice', style);
      applyStyle(style);
    }

    async function applyStyle(style) {
      try {
        await Plotly.relayout(plotlyDiv, { 'map.style': style });
      } catch (err) {
        console.error('Style change failed', err);
      }
    }

    // ── 3D Globe button: pass current map position ────────────────────────────
    const open3dBtn = document.getElementById('open-3d');
    if (open3dBtn) {
      open3dBtn.addEventListener('click', () => {
        const layout = plotlyDiv.layout;
        if (!layout || !layout.map || !layout.map.center) {
          location.href = 'cesium.html';
          return;
        }
        const c = layout.map.center;
        const z = layout.map.zoom ?? 5;
        location.href = `cesium.html?lat=${c.lat}&lon=${c.lon}&zoom=${z}`;
      });
    }

    // ── Restore position from 3D -> 2D return ────────────────────────────────
    const params = new URLSearchParams(window.location.search);
    const rlat   = parseFloat(params.get('lat'));
    const rlon   = parseFloat(params.get('lon'));
    const rzoom  = parseFloat(params.get('zoom'));
    const hasUrlPos = Number.isFinite(rlat) && Number.isFinite(rlon);

    if (hasUrlPos) {
      // Plotly's map initialises asynchronously — retry at several intervals
      // to guarantee the relayout sticks regardless of load speed.
      const applyPos = () => Plotly.relayout(plotlyDiv, {
        'map.center': { lat: rlat, lon: rlon },
        'map.zoom':   Number.isFinite(rzoom) ? rzoom : 5,
      });
      [100, 500, 1200].forEach(t => setTimeout(applyPos, t));
    }

    // ── Geolocation (auto, no button) ─────────────────────────────────────────
    let userTraceIndex = null;

    function doGeolocate(flyTo) {
      if (!navigator.geolocation) return;

      navigator.geolocation.getCurrentPosition(
        pos => {
          const { latitude, longitude } = pos.coords;

          if (userTraceIndex !== null) {
            Plotly.deleteTraces(plotlyDiv, userTraceIndex);
            userTraceIndex = null;
          }

          // Blue dot with white border — matches the 3D globe style
          const userTrace = {
            type: 'scattermap',
            mode: 'markers+text',
            lat: [latitude],
            lon: [longitude],
            text: ['You are here'],
            textposition: 'top center',
            textfont: { size: 15, color: 'white' },
            marker: {
              size: 20,
              color: '#4285F4',
              line: { width: 3, color: 'white' },
            },
            hovertemplate: `<b>Your Location</b><br>${latitude.toFixed(5)}\u00b0, ${longitude.toFixed(5)}\u00b0<extra></extra>`,
            name: 'My Location',
            showlegend: false,
          };

          Plotly.addTraces(plotlyDiv, userTrace).then(() => {
            userTraceIndex = plotlyDiv.data.length - 1;
          });

          if (flyTo) {
            Plotly.relayout(plotlyDiv, {
              'map.center': { lat: latitude, lon: longitude },
              'map.zoom': 10,
            });
          }
        },
        () => { /* silently ignore geolocation errors on auto-request */ },
        { enableHighAccuracy: false, timeout: 12000, maximumAge: 60000 }
      );
    }

    // Auto-geolocate on every page load.
    // Fly to location only on fresh loads; when returning from 3D the URL
    // params already set the position, so just show the dot.
    doGeolocate(!hasUrlPos);
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

/* === Buttons === */
#view-switcher,
#style-switcher {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: fixed;
  z-index: 10001;
}

#view-switcher {
  top: 12px;
  right: 12px;
  align-items: flex-end;
}

#style-switcher {
  top: 12px;
  left: 12px;
  gap: 6px;
}

#view-switcher button,
#style-switcher button {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: clamp(14px, 2vw, 18px);
  padding: clamp(9px, 1.6vw, 13px) clamp(13px, 2.2vw, 19px);
  border-radius: 9px;
  border: 1px solid rgba(100, 180, 255, 0.2);
  cursor: pointer;
  background: rgba(20, 35, 55, 0.88);
  backdrop-filter: blur(10px);
  color: white;
  transition: transform 0.15s, background 0.15s;
  white-space: nowrap;
}

#view-switcher button:hover,
#style-switcher button:hover {
  background: rgba(40, 70, 110, 0.95);
  border-color: rgba(100, 180, 255, 0.45);
  transform: scale(1.04);
}

#style-switcher .hint {
  font-size: clamp(10px, 1.2vw, 13px);
  opacity: 0.6;
  color: white;
}

/* Stats bar */
#stats-bar-2d {
  position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%);
  background: rgba(12, 22, 38, 0.82);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(100, 200, 255, 0.18);
  border-radius: 20px; padding: 7px 20px;
  color: rgba(190, 220, 255, 0.88);
  font-size: clamp(11px, 1.4vw, 14px);
  font-family: 'Inter', system-ui, sans-serif;
  z-index: 10001; white-space: nowrap;
  pointer-events: none;
}

/* Custom legend (fixed-position so it never disappears on zoom) */
#legend-2d {
  position: fixed; bottom: 52px; right: 16px;
  background: rgba(12,22,38,0.85); backdrop-filter: blur(10px);
  border: 1px solid rgba(100,200,255,0.18); border-radius: 11px;
  padding: 12px 16px; color: white;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 13px; z-index: 10001;
}
#legend-2d h4 { margin: 0 0 9px; font-size: 11px; color: rgba(160,210,255,0.75); text-transform: uppercase; letter-spacing: 0.8px; }
.leg-row { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
.leg-dot  { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* Mobile */
@media (max-width: 768px) {
  #view-switcher button,
  #style-switcher button {
    font-size: 20px;
    padding: 14px 22px;
    border-radius: 12px;
  }
  #style-switcher .hint { font-size: 14px; }
  #legend-2d {
    font-size: 15px;
    padding: 12px 16px;
  }
  #legend-2d h4 { font-size: 12px; }
  .leg-dot { width: 12px; height: 12px; }
}

/* Hover tooltip text */
.hoverlayer .hovertext {
  font-size: 200% !important;
  padding: 20px !important;
}
.hoverlayer .hovertext text {
  font-size: 15px !important;
}

</style>
"""


# Insert custom CSS into <head>
html_content = html_content.replace("<head>", "<head>\n" + custom_css, 1)

html_content = html_content.replace(
    "<body>",
    "<body>\n"
    + view_switcher_html + "\n"
    + style_selector_html + "\n"
    + legend_2d_html + "\n"
    + style_switcher_js,
    1
)

# Insert service worker script before </body>
html_content = html_content.replace("</body>", service_worker_script + "\n</body>", 1)

# Save the updated HTML
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)
