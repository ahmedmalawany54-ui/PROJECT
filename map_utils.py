"""Satellite map + field polygon helpers."""
import json
import math

import folium
import streamlit as st
from folium.plugins import Draw

ESRI = ("https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}")


@st.cache_resource(max_entries=10, show_spinner=False)
def build_map(lat, lng, polygon_json=None):
    """Cached per (lat, lng, polygon) so unrelated reruns don't rebuild the map."""
    m = folium.Map(location=[lat, lng], zoom_start=15, control_scale=True,
                   prefer_canvas=True, tiles=None)
    folium.TileLayer(tiles=ESRI, attr="Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics",
                     name="Satellite", overlay=False, control=True, show=True).add_to(m)
    folium.TileLayer(tiles="OpenStreetMap", name="Street Map", overlay=False,
                     control=True, show=False).add_to(m)

    if polygon_json:
        folium.GeoJson(
            json.loads(polygon_json), name="Field boundary",
            style_function=lambda _: {"color": "#34d399", "weight": 3,
                                      "fillColor": "#34d399", "fillOpacity": 0.15},
        ).add_to(m)

    folium.Marker(
        [lat, lng], tooltip="AEGIS analysis point",
        popup=folium.Popup(f"<b>AEGIS</b><br>{lat:.6f}, {lng:.6f}", max_width=240),
        icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
    ).add_to(m)

    Draw(export=False,
         draw_options={"polyline": False, "rectangle": True, "polygon": True,
                       "circle": False, "marker": False, "circlemarker": False},
         edit_options={"edit": True, "remove": True}).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    return m


def latest_polygon(drawings):
    """Most recent Polygon feature from st_folium's all_drawings, or None."""
    for feature in reversed(drawings or []):
        if feature.get("geometry", {}).get("type") == "Polygon":
            return feature
    return None


def polygon_stats(feature):
    """Returns (center_lat, center_lng, area_m2) for a GeoJSON Polygon feature."""
    ring = feature["geometry"]["coordinates"][0]
    pts = ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring
    clng = sum(p[0] for p in pts) / len(pts)  # GeoJSON order is [lng, lat]
    clat = sum(p[1] for p in pts) / len(pts)
    m_lat = 111320.0
    m_lng = 111320.0 * math.cos(math.radians(clat))
    xy = [((p[0] - clng) * m_lng, (p[1] - clat) * m_lat) for p in pts]
    area = abs(sum(xy[i][0] * xy[(i + 1) % len(xy)][1] - xy[(i + 1) % len(xy)][0] * xy[i][1]
                   for i in range(len(xy)))) / 2
    return clat, clng, area