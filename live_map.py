from __future__ import annotations

import json


def _first_tile_url(sources_config: dict) -> str:
    for source in sources_config.get("sources", {}).values():
        tiles = source.get("tiles") or []
        if tiles:
            return tiles[0]
    return ""


def build_maplibre_html(
    sources_config: dict,
    center_lon: float = -7.0,
    center_lat: float = 29.5,
    zoom: float = 5.0,
    height_px: int = 560,
) -> str:
    gee_tile_url = json.dumps(_first_tile_url(sources_config))
    layer_opacity = 0.75
    for layer in sources_config.get("layers", []):
        paint = layer.get("paint", {})
        if "raster-opacity" in paint:
            layer_opacity = float(paint["raster-opacity"])
            break

    start_lon = json.dumps(center_lon)
    start_lat = json.dumps(center_lat)
    start_zoom = int(round(zoom))
    opacity = json.dumps(max(0.0, min(1.0, layer_opacity)))

    return f"""
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: {height_px}px;
            overflow: hidden;
        }}
        #nrt-map {{
            position: relative;
            width: 100%;
            height: {height_px}px;
            overflow: hidden;
            border-radius: 16px;
            background: #dfe5dd;
            cursor: grab;
            user-select: none;
            font-family: Arial, sans-serif;
        }}
        #nrt-map.dragging {{
            cursor: grabbing;
        }}
        .tile {{
            position: absolute;
            width: 256px;
            height: 256px;
            image-rendering: auto;
        }}
        .base-tile {{
            z-index: 1;
        }}
        .gee-tile {{
            z-index: 2;
            opacity: {opacity};
        }}
        .nrt-controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 5;
            display: grid;
            gap: 6px;
        }}
        .nrt-controls button {{
            width: 34px;
            height: 34px;
            border: 1px solid #c9c9c9;
            border-radius: 8px;
            background: white;
            color: #2b2b2b;
            font-size: 20px;
            line-height: 1;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        .nrt-warning {{
            position: absolute;
            left: 10px;
            bottom: 10px;
            z-index: 6;
            max-width: calc(100% - 20px);
            background: #fff3f0;
            color: #7A3B2E;
            border: 1px solid #B5654A;
            padding: 7px 10px;
            border-radius: 8px;
            font: 12px/1.35 Arial, sans-serif;
        }}
    </style>

    <div id="nrt-map">
        <div class="nrt-controls">
            <button id="zoom-in" title="Zoom avant">+</button>
            <button id="zoom-out" title="Zoom arriere">-</button>
        </div>
        <div id="nrt-status" class="nrt-warning">Chargement de la carte live NRT...</div>
    </div>

    <script>
        const mapEl = document.getElementById('nrt-map');
        const statusEl = document.getElementById('nrt-status');
        const geeTemplate = {gee_tile_url};
        const tileSize = 256;
        let zoom = {start_zoom};
        let center = lonLatToWorld({start_lon}, {start_lat}, zoom);
        let isDragging = false;
        let dragStart = null;
        let dragCenter = null;
        let geeFailures = 0;
        let hasGeeSuccess = false;

        function lonLatToWorld(lon, lat, z) {{
            const scale = tileSize * Math.pow(2, z);
            const x = (lon + 180) / 360 * scale;
            const sinLat = Math.sin(lat * Math.PI / 180);
            const y = (0.5 - Math.log((1 + sinLat) / (1 - sinLat)) / (4 * Math.PI)) * scale;
            return {{x, y}};
        }}

        function tileUrl(template, z, x, y) {{
            return template
                .replace('{{z}}', z)
                .replace('{{x}}', x)
                .replace('{{y}}', y);
        }}

        function clearTiles() {{
            mapEl.querySelectorAll('.tile').forEach((tile) => tile.remove());
        }}

        function showStatus(message) {{
            statusEl.style.display = 'block';
            statusEl.innerText = message;
        }}

        function hideStatus() {{
            statusEl.style.display = 'none';
        }}

        function render() {{
            clearTiles();

            const width = mapEl.clientWidth;
            const height = mapEl.clientHeight;
            const scaleTiles = Math.pow(2, zoom);
            const startX = Math.floor((center.x - width / 2) / tileSize);
            const endX = Math.floor((center.x + width / 2) / tileSize);
            const startY = Math.floor((center.y - height / 2) / tileSize);
            const endY = Math.floor((center.y + height / 2) / tileSize);

            if (!geeTemplate) {{
                showStatus('maplibre_ldn_sources.json ne contient aucune URL de tuile GEE.');
            }} else {{
                hideStatus();
            }}

            for (let x = startX; x <= endX; x++) {{
                for (let y = startY; y <= endY; y++) {{
                    if (y < 0 || y >= scaleTiles) continue;
                    const wrappedX = ((x % scaleTiles) + scaleTiles) % scaleTiles;
                    const left = Math.round(x * tileSize - center.x + width / 2);
                    const top = Math.round(y * tileSize - center.y + height / 2);

                    const base = document.createElement('img');
                    base.className = 'tile base-tile';
                    base.src = `https://tile.openstreetmap.org/${{zoom}}/${{wrappedX}}/${{y}}.png`;
                    base.style.left = `${{left}}px`;
                    base.style.top = `${{top}}px`;
                    mapEl.appendChild(base);

                    if (geeTemplate) {{
                        const gee = document.createElement('img');
                        gee.className = 'tile gee-tile';
                        gee.src = tileUrl(geeTemplate, zoom, wrappedX, y);
                        gee.style.left = `${{left}}px`;
                        gee.style.top = `${{top}}px`;
                        gee.onload = () => {{
                            hasGeeSuccess = true;
                            hideStatus();
                        }};
                        gee.onerror = () => {{
                            geeFailures += 1;
                            gee.remove();
                            if (!hasGeeSuccess) {{
                                showStatus('Couche NRT GEE indisponible: token expire, acces bloque ou fichier maplibre_ldn_sources.json a regenerer via nrt_refresh(). La carte de fond reste interactive.');
                            }}
                        }};
                        mapEl.appendChild(gee);
                    }}
                }}
            }}
        }}

        document.getElementById('zoom-in').onclick = () => {{
            zoom = Math.min(zoom + 1, 12);
            center = {{x: center.x * 2, y: center.y * 2}};
            render();
        }};

        document.getElementById('zoom-out').onclick = () => {{
            zoom = Math.max(zoom - 1, 2);
            center = {{x: center.x / 2, y: center.y / 2}};
            render();
        }};

        mapEl.addEventListener('wheel', (event) => {{
            event.preventDefault();
            const nextZoom = event.deltaY < 0 ? Math.min(zoom + 1, 12) : Math.max(zoom - 1, 2);
            if (nextZoom === zoom) return;
            const factor = Math.pow(2, nextZoom - zoom);
            zoom = nextZoom;
            center = {{x: center.x * factor, y: center.y * factor}};
            render();
        }}, {{passive: false}});

        mapEl.addEventListener('mousedown', (event) => {{
            isDragging = true;
            mapEl.classList.add('dragging');
            dragStart = {{x: event.clientX, y: event.clientY}};
            dragCenter = {{...center}};
        }});

        window.addEventListener('mousemove', (event) => {{
            if (!isDragging) return;
            center = {{
                x: dragCenter.x - (event.clientX - dragStart.x),
                y: dragCenter.y - (event.clientY - dragStart.y)
            }};
            render();
        }});

        window.addEventListener('mouseup', () => {{
            isDragging = false;
            mapEl.classList.remove('dragging');
        }});

        window.addEventListener('resize', render);
        render();
    </script>
    """
