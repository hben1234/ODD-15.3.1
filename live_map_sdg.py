from __future__ import annotations
import json


def build_sdg_maplibre_html(
    sources_config: dict,
    geojson_data: dict | None = None,
    center_lon: float = -7.0,
    center_lat: float = 30.5,
    zoom: float = 6.0,
    height_px: int = 600,
    initial_opacity: float = 0.9,
) -> str:
    tile_url = ""
    for source in sources_config.get("sources", {}).values():
        tiles = source.get("tiles") or []
        if tiles:
            tile_url = tiles[0]
            break

    tile_url_json = json.dumps(tile_url)
    geojson_json  = json.dumps(geojson_data) if geojson_data else "null"
    opacity       = max(0.0, min(1.0, initial_opacity))
    zoom_int      = int(round(zoom))

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    html, body {{ width:100%; height:{height_px}px; overflow:hidden;
                  font-family:'Segoe UI','Aptos',Arial,sans-serif; }}
    #map {{
        position:relative; width:100%; height:{height_px}px;
        overflow:hidden; border-radius:16px; background:#111;
        cursor:grab; user-select:none;
    }}
    #map.dragging {{ cursor:grabbing; }}

    #skeleton {{
        position:absolute; inset:0; z-index:20;
        background: linear-gradient(110deg,#1a1a2e 30%,#16213e 50%,#1a1a2e 70%);
        background-size:200% 100%;
        animation: shimmer 1.4s infinite;
        border-radius:16px;
        display:flex; align-items:center; justify-content:center;
        flex-direction:column; gap:12px;
        transition: opacity 0.4s ease;
    }}
    #skeleton.hidden {{ opacity:0; pointer-events:none; }}
    @keyframes shimmer {{
        0%   {{ background-position:200% 0; }}
        100% {{ background-position:-200% 0; }}
    }}
    .skeleton-text {{
        color:rgba(255,255,255,0.55); font-size:13px; font-weight:600;
        letter-spacing:0.04em;
    }}
    .skeleton-spinner {{
        width:32px; height:32px; border:3px solid rgba(255,255,255,0.15);
        border-top-color:#0E7C66; border-radius:50%;
        animation: spin 0.8s linear infinite;
    }}
    @keyframes spin {{ to {{ transform:rotate(360deg); }} }}

    .tile {{
        position:absolute; width:256px; height:256px;
        image-rendering:crisp-edges;
        image-rendering:-moz-crisp-edges;
        image-rendering:pixelated;
    }}
    .base-tile {{ z-index:1; filter:brightness(0.4) saturate(0.3) contrast(1.1); }}
    .sdg-tile  {{ z-index:2; }}
    .boundaries {{
        position:absolute; top:0; left:0; width:100%; height:100%;
        z-index:3; pointer-events:none;
    }}
    .boundaries path {{
        fill:none; stroke:#ffffff; stroke-width:3;
        stroke-opacity:0.85; vector-effect:non-scaling-stroke;
    }}
    .controls {{
        position:absolute; top:12px; right:12px; z-index:10;
        display:flex; flex-direction:column; gap:8px;
    }}
    .controls button {{
        width:38px; height:38px; border:none; border-radius:8px;
        background:rgba(23,32,51,0.95); color:white;
        font-size:22px; font-weight:600; line-height:1;
        cursor:pointer; box-shadow:0 4px 12px rgba(0,0,0,0.4);
        transition:all 0.2s; backdrop-filter:blur(8px);
    }}
    .controls button:hover {{
        background:rgba(14,124,102,0.95); transform:translateY(-1px);
    }}
    .legend {{
        position:absolute; bottom:60px; right:12px; z-index:10;
        background:rgba(23,32,51,0.95); border:1px solid rgba(14,124,102,0.4);
        border-radius:14px; padding:16px 18px;
        box-shadow:0 8px 24px rgba(0,0,0,0.5); min-width:200px;
        backdrop-filter:blur(12px);
    }}
    .legend-title {{
        font-weight:800; margin-bottom:12px; color:#fff; font-size:14px;
        border-bottom:2px solid #0E7C66; padding-bottom:6px;
    }}
    .legend-item  {{ display:flex; align-items:center; margin:8px 0; gap:10px; }}
    .legend-color {{
        width:32px; height:20px; border-radius:5px;
        border:1px solid rgba(255,255,255,0.2); flex-shrink:0;
        box-shadow:0 2px 6px rgba(0,0,0,0.3);
    }}
    .legend-label {{ color:#e0e0e0; font-size:13px; font-weight:500; flex:1; }}
    .info-box {{
        position:absolute; top:12px; left:12px; z-index:10;
        background:rgba(23,32,51,0.95); border:1px solid rgba(14,124,102,0.4);
        border-radius:10px; padding:10px 14px; font-size:12px; color:#e0e0e0;
        box-shadow:0 4px 12px rgba(0,0,0,0.4); backdrop-filter:blur(12px);
    }}
    .info-box strong {{ color:#0E7C66; font-weight:700; }}
    .warning-box {{
        position:absolute; left:12px; bottom:12px; z-index:10;
        max-width:calc(100% - 240px); background:rgba(183,28,28,0.95);
        color:#fff; border:1px solid rgba(220,38,38,0.8);
        padding:10px 14px; border-radius:10px; font-size:11px;
        line-height:1.5; display:none; backdrop-filter:blur(8px);
    }}
    .zoom-indicator {{
        position:absolute; bottom:12px; right:12px; z-index:5;
        background:rgba(23,32,51,0.8); color:#e0e0e0;
        padding:6px 12px; border-radius:8px; font-size:11px;
        font-weight:600; backdrop-filter:blur(8px);
    }}
</style>
</head>
<body>
<div id="map">
    <div id="skeleton">
        <div class="skeleton-spinner"></div>
        <div class="skeleton-text">Chargement de la carte SDG 15.3.1…</div>
    </div>
    <svg class="boundaries" id="boundaries-svg"></svg>
    <div class="controls">
        <button id="zoom-in" title="Zoom avant">+</button>
        <button id="zoom-out" title="Zoom arrière">−</button>
    </div>
    <div class="legend">
        <div class="legend-title">SDG 15.3.1</div>
        <div class="legend-item"><div class="legend-color" style="background:#a50026"></div><div class="legend-label">Dégradé</div></div>
        <div class="legend-item"><div class="legend-color" style="background:#ffffbf"></div><div class="legend-label">Stable</div></div>
        <div class="legend-item"><div class="legend-color" style="background:#1a9850"></div><div class="legend-label">Amélioré</div></div>
    </div>
    <div class="info-box"><strong>SDG 15.3.1</strong> • Statut officiel (2016-2025)</div>
    <div id="warning" class="warning-box"></div>
    <div id="zoom-level" class="zoom-indicator">Zoom: {zoom_int}</div>
</div>

<script>
    const TILE_SIZE    = 256;
    const GEE_CLASS    = 'sdg-tile';
    const mapEl        = document.getElementById('map');
    const warningEl    = document.getElementById('warning');
    const zoomEl       = document.getElementById('zoom-level');
    const boundariesSvg= document.getElementById('boundaries-svg');
    const skeletonEl   = document.getElementById('skeleton');
    const geeTemplate  = {tile_url_json};
    const geojsonData  = {geojson_json};

    let zoom           = {zoom_int};
    let center         = lonLatToWorld({center_lon}, {center_lat}, zoom);
    let isDragging     = false;
    let dragStart      = null;
    let dragCenter     = null;
    let currentOpacity = {opacity};
    let renderToken    = 0;
    let panTimer       = null;
    let skeletonGone   = false;

    const CACHE_MAX = 1024;
    const tileCache = new Map();

    function cacheGet(url) {{
        if (!tileCache.has(url)) return null;
        const img = tileCache.get(url);
        tileCache.delete(url);
        tileCache.set(url, img);
        return img;
    }}
    function cacheSet(url, img) {{
        if (tileCache.size >= CACHE_MAX)
            tileCache.delete(tileCache.keys().next().value);
        tileCache.set(url, img);
    }}

    function lonLatToWorld(lon, lat, z) {{
        const scale = TILE_SIZE * Math.pow(2, z);
        const x = (lon + 180) / 360 * scale;
        const sinLat = Math.sin(lat * Math.PI / 180);
        const y = (0.5 - Math.log((1 + sinLat) / (1 - sinLat)) / (4 * Math.PI)) * scale;
        return {{x, y}};
    }}
    function worldToLonLat(wx, wy, z) {{
        const scale = TILE_SIZE * Math.pow(2, z);
        const lon = wx / scale * 360 - 180;
        const n   = Math.PI - 2 * Math.PI * wy / scale;
        const lat = 180 / Math.PI * Math.atan(0.5 * (Math.exp(n) - Math.exp(-n)));
        return {{lon, lat}};
    }}
    function tileUrl(tmpl, z, x, y) {{
        return tmpl.replace('{{z}}', z).replace('{{x}}', x).replace('{{y}}', y);
    }}

    function showWarning(msg) {{ warningEl.style.display='block'; warningEl.innerHTML=msg; }}
    function hideWarning()    {{ warningEl.style.display='none'; }}
    function updateZoom()     {{ zoomEl.textContent='Zoom: '+zoom; }}
    function hideSkeleton() {{
        if (skeletonGone) return;
        skeletonGone = true;
        skeletonEl.classList.add('hidden');
        setTimeout(() => skeletonEl.remove(), 450);
    }}

    function projectCoord(lon, lat) {{
        const w = lonLatToWorld(lon, lat, zoom);
        return {{ x: w.x - center.x + mapEl.clientWidth/2,
                  y: w.y - center.y + mapEl.clientHeight/2 }};
    }}
    function drawBoundaries() {{
        if (!geojsonData?.features) return;
        boundariesSvg.innerHTML = '';
        const W = mapEl.clientWidth, H = mapEl.clientHeight;
        boundariesSvg.setAttribute('viewBox', '0 0 '+W+' '+H);
        geojsonData.features.forEach(f => {{
            const g = f.geometry; if (!g) return;
            const drawPoly = rings => rings.forEach(ring => {{
                const d = ring.map(c => projectCoord(c[0],c[1]))
                              .map((p,i) => (i?'L':'M')+p.x+','+p.y).join(' ')+' Z';
                const path = document.createElementNS('http://www.w3.org/2000/svg','path');
                path.setAttribute('d', d);
                boundariesSvg.appendChild(path);
            }});
            if (g.type==='Polygon') drawPoly(g.coordinates);
            else if (g.type==='MultiPolygon') g.coordinates.forEach(p => drawPoly(p));
        }});
    }}

    function loadTile(url) {{
        const hit = cacheGet(url);
        if (hit) return Promise.resolve(hit);
        return new Promise(resolve => {{
            const img = new Image();
            img.onload  = () => {{ cacheSet(url, img); resolve(img); }};
            img.onerror = () => resolve(null);
            img.src = url;
        }});
    }}

    function visibleTileCoords(margin) {{
        const W = mapEl.clientWidth, H = mapEl.clientHeight;
        const scale = Math.pow(2, zoom);
        const x0 = Math.floor((center.x - W/2) / TILE_SIZE) - margin;
        const x1 = Math.floor((center.x + W/2) / TILE_SIZE) + margin;
        const y0 = Math.floor((center.y - H/2) / TILE_SIZE) - margin;
        const y1 = Math.floor((center.y + H/2) / TILE_SIZE) + margin;
        const cx = (x0+x1)/2, cy = (y0+y1)/2;
        const coords = [];
        for (let x=x0; x<=x1; x++) {{
            for (let y=y0; y<=y1; y++) {{
                if (y<0 || y>=scale) continue;
                const wx   = ((x%scale)+scale)%scale;
                const left = Math.round(x*TILE_SIZE - center.x + W/2);
                const top  = Math.round(y*TILE_SIZE - center.y + H/2);
                const dist = (x-cx)**2 + (y-cy)**2;
                coords.push({{x, y, wx, left, top, dist}});
            }}
        }}
        coords.sort((a,b) => a.dist - b.dist);
        return coords;
    }}

    function render() {{
        const myToken = ++renderToken;
        mapEl.querySelectorAll('.tile').forEach(t => t.remove());
        updateZoom();
        drawBoundaries();

        if (!geeTemplate) {{
            showWarning('⚠️ Aucune URL de tuile SDG.<br>Exécutez : <code>python refresh_sdg_tiles.py</code>');
            return;
        }}

        const coords        = visibleTileCoords(1);
        const prefetchCoords= visibleTileCoords(2);

        let geeLoaded=0, geeFailed=0;
        const geeTotal = coords.length;

        coords.forEach(({{wx, y, left, top}}) => {{
            const osmUrl = 'https://tile.openstreetmap.org/'+zoom+'/'+wx+'/'+y+'.png';
            loadTile(osmUrl).then(img => {{
                if (myToken !== renderToken || !img) return;
                const el = img.cloneNode();
                el.className  = 'tile base-tile';
                el.style.left = left+'px'; el.style.top = top+'px';
                mapEl.insertBefore(el, boundariesSvg);
            }});

            const gUrl = tileUrl(geeTemplate, zoom, wx, y);
            loadTile(gUrl).then(img => {{
                if (myToken !== renderToken) return;
                if (img) {{
                    geeLoaded++;
                    const el = img.cloneNode();
                    el.className    = 'tile '+GEE_CLASS;
                    el.style.left   = left+'px'; el.style.top = top+'px';
                    el.style.opacity= currentOpacity;
                    mapEl.insertBefore(el, boundariesSvg);
                    hideSkeleton();
                    hideWarning();
                }} else {{
                    geeFailed++;
                }}
                if (geeLoaded+geeFailed===geeTotal && geeLoaded===0)
                    showWarning('❌ Tuiles indisponibles — token expiré ?<br>Régénérez : <code>python refresh_sdg_tiles.py</code>');
            }});
        }});

        prefetchCoords.forEach(({{wx, y}}) => {{
            const gUrl = tileUrl(geeTemplate, zoom, wx, y);
            if (!cacheGet(gUrl)) loadTile(gUrl);
        }});
    }}

    function setOpacity(v) {{
        currentOpacity = Math.max(0, Math.min(1, v));
        document.querySelectorAll('.'+GEE_CLASS).forEach(t => {{ t.style.opacity=currentOpacity; }});
    }}

    function zoomTo(nz) {{
        if (nz===zoom) return;
        const geo = worldToLonLat(center.x, center.y, zoom);
        zoom   = nz;
        center = lonLatToWorld(geo.lon, geo.lat, zoom);
        render();
    }}

    document.getElementById('zoom-in').onclick  = () => zoomTo(Math.min(zoom+1, 12));
    document.getElementById('zoom-out').onclick = () => zoomTo(Math.max(zoom-1, 2));

    mapEl.addEventListener('wheel', e => {{
        e.preventDefault();
        zoomTo(e.deltaY < 0 ? Math.min(zoom+1,12) : Math.max(zoom-1,2));
    }}, {{passive:false}});

    mapEl.addEventListener('mousedown', e => {{
        isDragging=true; mapEl.classList.add('dragging');
        dragStart={{x:e.clientX, y:e.clientY}}; dragCenter={{...center}};
    }});
    window.addEventListener('mousemove', e => {{
        if (!isDragging) return;
        center = {{ x: dragCenter.x-(e.clientX-dragStart.x),
                    y: dragCenter.y-(e.clientY-dragStart.y) }};
        drawBoundaries(); updateZoom();
        clearTimeout(panTimer); panTimer=setTimeout(render, 60);
    }});
    window.addEventListener('mouseup', () => {{
        if (!isDragging) return;
        isDragging=false; mapEl.classList.remove('dragging');
        clearTimeout(panTimer); render();
    }});

    window.addEventListener('message', e => {{
        if (e.data?.type==='set-opacity') setOpacity(e.data.value);
    }});
    window.addEventListener('resize', render);

    render();
</script>
</body>
</html>"""
