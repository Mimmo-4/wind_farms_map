"""
Patch index.html with UI improvements without needing to regenerate from scratch.
Run: python scripts/patch_index.py
"""
import re

html_file = "index.html"

with open(html_file, "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. Upgrade button CSS ────────────────────────────────────────────────────
old_btn_css = """/* === Buttons (desktop default) === */
#view-switcher,
#style-switcher {
  position: fixed;
  z-index: 10001;
}

#view-switcher {
  top: 12px;
  right: 12px;
}

#style-switcher {
  top: 12px;
  left: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

#view-switcher button,
#style-switcher button {
  font-size: 16px;
  padding: 8px 14px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  background: #2c3e50;
  color: white;
}

#style-switcher .hint {
  font-size: 11px;
  margin-top: 4px;
  opacity: 0.7;
}

/* === MOBILE: BIG touch-friendly buttons === */
@media (max-width: 768px) {
  #view-switcher button,
  #style-switcher button {
    font-size: 22px;
    padding: 16px 22px;
    border-radius: 12px;
  }

  #style-switcher .hint {
    font-size: 14px;
  }
}

/* Bigger hover text on mobile */
.hoverlayer .hovertext {
  font-size: 200% !important;
  padding: 20px !important;
}"""

new_btn_css = """/* === Buttons === */
#view-switcher,
#style-switcher {
  position: fixed;
  z-index: 10001;
}

#view-switcher {
  top: 12px;
  right: 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

#style-switcher {
  top: 12px;
  left: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

#view-switcher button,
#style-switcher button {
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
  margin-top: 2px;
  opacity: 0.6;
  color: white;
}

/* Stats bar — bottom center */
#stats-bar-2d {
  position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%);
  background: rgba(12, 22, 38, 0.82);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(100, 200, 255, 0.18);
  border-radius: 20px; padding: 7px 20px;
  color: rgba(190, 220, 255, 0.88);
  font-size: clamp(11px, 1.4vw, 14px);
  font-family: system-ui, sans-serif;
  z-index: 10001; white-space: nowrap;
  pointer-events: none;
}

/* Location button (inside style-switcher) */
#btn-my-location {
  margin-top: 4px;
}

/* User location marker layer */
#user-location-dot {
  width: 18px; height: 18px;
  border-radius: 50%;
  background: #3399ff;
  border: 3px solid white;
  box-shadow: 0 0 10px #3399ff88;
  pointer-events: none;
}

/* === MOBILE === */
@media (max-width: 768px) {
  #view-switcher button,
  #style-switcher button {
    font-size: 20px;
    padding: 15px 20px;
    border-radius: 12px;
  }
  #style-switcher .hint {
    font-size: 13px;
  }
}

/* Bigger hover text */
.hoverlayer .hovertext {
  font-size: 200% !important;
  padding: 20px !important;
}
.hoverlayer .hovertext text {
  font-size: 15px !important;
}"""

if old_btn_css in html:
    html = html.replace(old_btn_css, new_btn_css, 1)
    print("✓ CSS upgraded")
else:
    print("⚠ CSS block not found — skipping CSS upgrade")


# ── 2. Fix 3D Globe button (add id so JS can attach position) ───────────────
old_view = """<div id="view-switcher">
  <button onclick="location.href='cesium.html'">
    🌍 3D Globe
  </button>
</div>"""

new_view = """<div id="view-switcher">
  <button id="open-3d">🌍 3D Globe</button>
</div>"""

if old_view in html:
    html = html.replace(old_view, new_view, 1)
    print("✓ View switcher button fixed")
else:
    # Already has id="open-3d" (regenerated from current main.py)
    print("⚠ Old view-switcher not found — may already be up-to-date")


# ── 3. Add location button to style-switcher ─────────────────────────────────
old_style_sw = """<div id="style-switcher">
  <button id="change-style-btn">
    🗺️ Change style
  </button>
  <small class="hint">Shift+S</small>
</div>"""

new_style_sw = """<div id="style-switcher">
  <button id="change-style-btn">🗺️ Change style</button>
  <small class="hint">Shift+S</small>
  <button id="btn-my-location">📍 My Location</button>
</div>"""

if old_style_sw in html:
    html = html.replace(old_style_sw, new_style_sw, 1)
    print("✓ Location button added")
else:
    print("⚠ Style-switcher not found — skipping location button")


# ── 4. Add stats bar div after <body> ─────────────────────────────────────────
old_body_start = "<body>\n\n<div id=\"view-switcher\">"
new_body_start = """<body>

<div id="stats-bar-2d">🌬️ 246,229 turbines worldwide</div>

<div id="view-switcher">"""

if old_body_start in html:
    html = html.replace(old_body_start, new_body_start, 1)
    print("✓ Stats bar added")
else:
    print("⚠ Body start pattern not found — skipping stats bar")


# ── 5. Add new JS block before </body> ───────────────────────────────────────
geoloc_and_fix_js = """
<script>
(function () {

  // ── Apply map position from URL params (when returning from 3D view) ──────
  function ready(fn) {
    document.readyState !== 'loading'
      ? fn()
      : document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    const params = new URLSearchParams(window.location.search);
    const lat  = parseFloat(params.get('lat'));
    const lon  = parseFloat(params.get('lon'));
    const zoom = parseFloat(params.get('zoom'));

    const plotlyDiv = document.querySelector('.js-plotly-plot, .plotly');
    if (!plotlyDiv || !window.Plotly) return;

    // Restore position from 3D → 2D navigation
    if (Number.isFinite(lat) && Number.isFinite(lon)) {
      Plotly.relayout(plotlyDiv, {
        'map.center': { lat, lon },
        'map.zoom':   Number.isFinite(zoom) ? zoom : 5
      });
    }

    // ── Fix 3D Globe button: pass current Plotly map center ─────────────────
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

    // ── Geolocation ───────────────────────────────────────────────────────────
    const locBtn = document.getElementById('btn-my-location');
    if (!locBtn) return;

    let userTraceIndex = null;  // track which trace index is the user marker

    locBtn.addEventListener('click', () => {
      if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        return;
      }
      locBtn.textContent = '📍 Locating…';
      locBtn.disabled = true;

      navigator.geolocation.getCurrentPosition(
        pos => {
          const { latitude, longitude } = pos.coords;

          // Remove previous user location trace
          if (userTraceIndex !== null) {
            Plotly.deleteTraces(plotlyDiv, userTraceIndex);
            userTraceIndex = null;
          }

          // Add user location as a new trace
          const userTrace = {
            type: 'scattermapbox',
            mode: 'markers+text',
            lat: [latitude],
            lon: [longitude],
            text: ['📍 You are here'],
            textposition: 'top center',
            textfont: { size: 14, color: 'white' },
            marker: {
              size: 20,
              color: '#3399ff',
              symbol: 'circle',
              opacity: 1,
            },
            hovertemplate: `<b>Your Location</b><br>${latitude.toFixed(5)}°, ${longitude.toFixed(5)}°<extra></extra>`,
            name: 'My Location',
            showlegend: false,
          };

          Plotly.addTraces(plotlyDiv, userTrace).then(() => {
            userTraceIndex = plotlyDiv.data.length - 1;
          });

          // Fly to user location
          Plotly.relayout(plotlyDiv, {
            'map.center': { lat: latitude, lon: longitude },
            'map.zoom': 10
          });

          locBtn.textContent = '📍 My Location';
          locBtn.disabled = false;
        },
        err => {
          const msgs = { 1: 'Permission denied.', 2: 'Position unavailable.', 3: 'Timed out.' };
          alert('Could not get your location: ' + (msgs[err.code] || err.message));
          locBtn.textContent = '📍 My Location';
          locBtn.disabled = false;
        },
        { enableHighAccuracy: false, timeout: 12000, maximumAge: 60000 }
      );
    });
  });

})();
</script>
"""

# Insert before the service worker script (which is near </body>)
sw_marker = "<script>\n    if ('serviceWorker' in navigator)"
if sw_marker in html:
    html = html.replace(sw_marker, geoloc_and_fix_js + "\n" + sw_marker, 1)
    print("✓ Geolocation + 3D button JS injected")
else:
    # Fallback: insert before </body>
    html = html.replace("</body>", geoloc_and_fix_js + "\n</body>", 1)
    print("✓ Geolocation + 3D button JS injected (fallback position)")


with open(html_file, "w", encoding="utf-8") as f:
    f.write(html)

print("\n✅ index.html patched successfully!")
print("   Serve with: python -m http.server 8080")
print("   Then open:  http://localhost:8080/index.html")
