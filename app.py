from __future__ import annotations

import json
import math
import os
from datetime import date, timedelta
from typing import Any

import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components

from folium.plugins import Draw, Fullscreen, MousePosition
from pyproj import Geod
from streamlit_folium import st_folium


# ============================================================
# AEGIS 2.0 | AGRICULTURAL INTELLIGENCE PLATFORM
# Streamlit + CesiumJS + Leaflet + Open-Meteo + NASA POWER
# ============================================================

st.set_page_config(
    page_title="AEGIS 2.0 | Agricultural Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- CONFIGURATION -------------------------

API_TIMEOUT = 30

HEADERS = {
    "User-Agent": "AEGIS-Agricultural-Intelligence/2.0"
}

ESRI_IMAGERY = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "World_Imagery/MapServer/tile/{z}/{y}/{x}"
)

ESRI_LABELS = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
)

CESIUM_TOKEN = (
    st.secrets.get("CESIUM_ION_TOKEN", "")
    if hasattr(st, "secrets")
    else ""
) or os.getenv("CESIUM_ION_TOKEN", "")

GEOD = Geod(ellps="WGS84")


# -------------------- CROP DATABASE ------------------------

CROPS = {
    "طماطم": {"kc": 1.15, "root": 0.60, "depletion": 0.40},
    "قمح": {"kc": 1.05, "root": 1.00, "depletion": 0.55},
    "ذرة": {"kc": 1.20, "root": 0.90, "depletion": 0.50},
    "باذنجان": {"kc": 1.05, "root": 0.60, "depletion": 0.40},
    "بطاطس": {"kc": 1.10, "root": 0.50, "depletion": 0.35},
    "قطن": {"kc": 1.15, "root": 1.20, "depletion": 0.60},
    "أرز": {"kc": 1.20, "root": 0.50, "depletion": 0.20},
    "محصول آخر": {"kc": 1.00, "root": 0.60, "depletion": 0.45},
}

STAGES = {
    "تأسيس / إنبات": 0.65,
    "نمو خضري": 0.90,
    "إزهار / إثمار": 1.00,
    "نضج": 0.80,
}


# -------------------- DESIGN SYSTEM ------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #070b10;
    --surface: #101820;
    --surface2: #151f29;
    --border: rgba(151, 190, 169, .13);
    --green: #75e5a1;
    --green2: #30c879;
    --text: #edf5ef;
    --muted: #8fa49a;
}

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
}

.stApp {
    background:
      radial-gradient(ellipse at 80% 0%, rgba(31,111,75,.15), transparent 32%),
      radial-gradient(ellipse at 0% 75%, rgba(28,85,67,.12), transparent 35%),
      #070b10;
    color: var(--text);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#101a21,#0a1117);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.2rem;
}

section.main > div {
    max-width: 1750px;
    padding: 1.5rem 2rem 3rem;
}

h1,h2,h3,h4 {
    color: var(--text);
    font-weight: 800;
}

h1 {
    letter-spacing: -.04em;
}

h2 {
    font-size: 1.35rem;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg,#14231d,#101820);
    border: 1px solid var(--border);
    border-radius: 17px;
    padding: 17px;
    box-shadow: 0 12px 32px rgba(0,0,0,.16);
    transition: .2s;
}

[data-testid="stMetric"]:hover {
    border-color: rgba(117,229,161,.4);
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: #9aafa3;
}

[data-testid="stMetricValue"] {
    color: var(--green);
    font-family: 'Manrope','Cairo',sans-serif;
    font-weight: 800;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(17,28,36,.70);
    border: 1px solid var(--border);
    border-radius: 19px;
}

.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(120deg,#75e5a1,#32c87b);
    color: #07160e;
    border: none;
    border-radius: 11px;
    font-weight: 800;
    min-height: 42px;
    transition: .2s;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #a0f3bd;
    color: #06150c;
    transform: translateY(-2px);
}

[data-baseweb="input"] > div,
[data-baseweb="select"] > div {
    background: #111c24;
    border-color: var(--border);
    border-radius: 10px;
    color: white;
}

[data-testid="stTabs"] button {
    font-weight: 700;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 13px;
}

[data-testid="stAlert"] {
    border-radius: 13px;
}

hr {
    border-color: var(--border);
}

.aegis-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    padding: 25px 28px;
    border-radius: 21px;
    border: 1px solid rgba(117,229,161,.18);
    background:
      radial-gradient(circle at 10% 50%,rgba(48,200,121,.17),transparent 35%),
      linear-gradient(120deg,#14251e,#101820 65%,#0d171d);
    margin-bottom: 23px;
}

.aegis-brand {
    font-family: 'Manrope','Cairo',sans-serif;
    font-size: 31px;
    font-weight: 900;
    letter-spacing: 2px;
    color: white;
}

.aegis-brand span {
    color: var(--green);
}

.aegis-subtitle {
    color: #9bb4a5;
    font-size: 12px;
    margin-top: 5px;
}

.aegis-status {
    color: var(--green);
    border: 1px solid rgba(117,229,161,.25);
    background: rgba(48,200,121,.09);
    padding: 8px 14px;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 800;
}

.section-label {
    color: #75e5a1;
    font-size: 11px;
    font-family: 'Manrope','Cairo',sans-serif;
    letter-spacing: 2px;
    font-weight: 800;
    margin-bottom: 7px;
}

.map-frame {
    border: 1px solid rgba(117,229,161,.20);
    border-radius: 17px;
    overflow: hidden;
}

.sidebar-brand {
    color: #75e5a1;
    font-family: 'Manrope','Cairo',sans-serif;
    font-size: 23px;
    font-weight: 900;
    letter-spacing: 2px;
}

@media(max-width:700px) {
    section.main > div {
        padding: 1rem .65rem 2rem;
    }

    .aegis-header {
        padding: 17px;
    }

    .aegis-brand {
        font-size: 24px;
    }
}
</style>
""", unsafe_allow_html=True)


# -------------------- SESSION STATE ------------------------

DEFAULTS = {
    "lat": 30.4167,
    "lon": 31.5667,
    "place_label": "بلبيس، مصر",
    "location_choices": [],
    "field_polygon": None,
    "field_area": 2.205,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------- API FUNCTIONS ------------------------

@st.cache_data(ttl=1800, show_spinner=False)
def get_weather(lat: float, lon: float) -> dict:

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "precipitation,wind_speed_10m"
        ),
        "hourly": (
            "temperature_2m,relative_humidity_2m,"
            "precipitation,soil_moisture_0_to_1cm,"
            "et0_fao_evapotranspiration"
        ),
        "daily": (
            "temperature_2m_max,temperature_2m_min,"
            "precipitation_sum,et0_fao_evapotranspiration,"
            "precipitation_probability_max"
        ),
        "forecast_days": 7,
        "past_days": 7,
        "timezone": "auto",
        "wind_speed_unit": "ms",
    }

    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params=params,
        timeout=API_TIMEOUT,
        headers=HEADERS,
    )

    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=86400, show_spinner=False)
def get_nasa_power(
    lat: float,
    lon: float,
    start: str,
    end: str
) -> dict:

    params = {
        "parameters": (
            "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,"
            "RH2M,ALLSKY_SFC_SW_DWN"
        ),
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON",
        "time-standard": "UTC",
    }

    response = requests.get(
        "https://power.larc.nasa.gov/api/temporal/daily/point",
        params=params,
        timeout=API_TIMEOUT,
        headers=HEADERS,
    )

    response.raise_for_status()

    payload = response.json()

    if "properties" not in payload:
        raise ValueError("NASA POWER returned invalid data.")

    return payload


@st.cache_data(ttl=86400, show_spinner=False)
def geocode(place: str) -> list:

    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": place,
            "count": 8,
            "language": "ar",
            "format": "json",
        },
        timeout=API_TIMEOUT,
        headers=HEADERS,
    )

    response.raise_for_status()

    return response.json().get("results", [])


def nasa_frame(payload: dict) -> pd.DataFrame:

    series = payload["properties"]["parameter"]

    frames = []

    for key, values in series.items():

        item = pd.Series(values, name=key)

        item.index = pd.to_datetime(
            item.index,
            format="%Y%m%d",
            errors="coerce"
        )

        frames.append(item)

    if not frames:
        return pd.DataFrame()

    frame = pd.concat(frames, axis=1).sort_index()

    return frame.replace(-999, float("nan"))


def safe_float(value: Any) -> float | None:

    try:
        number = float(value)

        if math.isfinite(number):
            return number

    except (TypeError, ValueError):
        pass

    return None


def polygon_area_ha(geometry: dict) -> float:

    coordinates = geometry["coordinates"][0]

    lon = [point[0] for point in coordinates]
    lat = [point[1] for point in coordinates]

    area, _ = GEOD.polygon_area_perimeter(lon, lat)

    return abs(area) / 10000


# -------------------- MAP: 2D SATELLITE ---------------------

def render_satellite_map(
    lat: float,
    lon: float,
    polygon: dict | None
):

    map_2d = folium.Map(
        location=[lat, lon],
        zoom_start=17,
        tiles=None,
        control_scale=True,
        prefer_canvas=True,
    )

    folium.TileLayer(
        tiles=ESRI_IMAGERY,
        attr="Esri World Imagery",
        name="Satellite Imagery",
        overlay=False,
        control=True,
        max_zoom=19,
    ).add_to(map_2d)

    folium.TileLayer(
        tiles=ESRI_LABELS,
        attr="Esri Reference Labels",
        name="Places & Boundaries",
        overlay=True,
        control=True,
        opacity=0.85,
    ).add_to(map_2d)

    folium.Marker(
        [lat, lon],
        tooltip="AEGIS FIELD CENTER",
        popup=f"{lat:.6f}, {lon:.6f}",
        icon=folium.Icon(
            color="green",
            icon="leaf",
            prefix="fa"
        )
    ).add_to(map_2d)

    folium.Circle(
        [lat, lon],
        radius=40,
        color="#48ec9a",
        weight=2,
        fill=True,
        fill_color="#48ec9a",
        fill_opacity=.13,
    ).add_to(map_2d)

    if polygon:

        folium.GeoJson(
            polygon,
            name="Field Boundary",
            style_function=lambda feature: {
                "color": "#62f5a3",
                "weight": 3,
                "fillColor": "#42c984",
                "fillOpacity": 0.18,
            }
        ).add_to(map_2d)

    Draw(
        export=True,
        filename="aegis_field_boundary.geojson",
        draw_options={
            "polyline": False,
            "rectangle": True,
            "polygon": True,
            "circle": False,
            "circlemarker": False,
            "marker": False,
        },
        edit_options={
            "edit": True,
            "remove": True,
        }
    ).add_to(map_2d)

    Fullscreen(
        position="topleft",
        title="Full Screen",
        title_cancel="Exit Full Screen",
    ).add_to(map_2d)

    MousePosition(
        position="bottomright",
        separator=" | ",
        prefix="COORDINATES",
        num_digits=6,
    ).add_to(map_2d)

    folium.LayerControl(
        position="topright",
        collapsed=False
    ).add_to(map_2d)

    return map_2d


# -------------------- MAP: 3D CESIUM -----------------------

def render_3d_map(
    lat: float,
    lon: float,
    token: str,
    polygon: dict | None
):

    safe_token = json.dumps(token)
    safe_lat = json.dumps(float(lat))
    safe_lon = json.dumps(float(lon))
    safe_polygon = json.dumps(polygon or {})

    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<script src="https://cesium.com/downloads/cesiumjs/releases/1.127/Build/Cesium/Cesium.js"></script>

<link href="https://cesium.com/downloads/cesiumjs/releases/1.127/Build/Cesium/Widgets/widgets.css" rel="stylesheet">

<style>
html,body,#cesiumContainer {
    width:100%;
    height:100%;
    margin:0;
    padding:0;
    overflow:hidden;
    background:#080e14;
}

.cesium-viewer-toolbar {
    top:12px !important;
    right:12px !important;
}

.cesium-viewer-bottom {
    display:none !important;
}

#map-status {
    position:absolute;
    top:13px;
    left:13px;
    z-index:10;
    padding:9px 13px;
    border:1px solid rgba(117,229,161,.3);
    border-radius:9px;
    background:rgba(8,18,15,.85);
    color:#8cf0ae;
    font:12px Arial,sans-serif;
    pointer-events:none;
}

#map-error {
    position:absolute;
    bottom:14px;
    left:14px;
    z-index:20;
    max-width:85%;
    padding:9px 12px;
    border-radius:8px;
    background:rgba(12,20,25,.9);
    color:#ffd28a;
    font:12px Arial,sans-serif;
    display:none;
}
</style>
</head>

<body>

<div id="cesiumContainer"></div>

<div id="map-status">AEGIS · 3D EARTH</div>
<div id="map-error"></div>

<script>
(async function() {

    const TOKEN = __TOKEN__;
    const LAT = __LAT__;
    const LON = __LON__;
    const POLYGON = __POLYGON__;

    const errorBox = document.getElementById("map-error");

    function showError(message) {
        errorBox.innerText = message;
        errorBox.style.display = "block";
    }

    Cesium.Ion.defaultAccessToken = TOKEN;

    const viewer = new Cesium.Viewer("cesiumContainer", {

        animation: false,
        timeline: false,
        geocoder: false,
        homeButton: true,
        sceneModePicker: true,
        baseLayerPicker: false,
        navigationHelpButton: true,
        fullscreenButton: true,
        infoBox: true,
        selectionIndicator: true,

        terrainProvider: new Cesium.EllipsoidTerrainProvider(),

        baseLayer: new Cesium.ImageryLayer(
            new Cesium.UrlTemplateImageryProvider({
                url:
                "https://server.arcgisonline.com/ArcGIS/rest/services/" +
                "World_Imagery/MapServer/tile/{z}/{y}/{x}",
                credit: "Esri World Imagery",
                maximumLevel: 19
            })
        ),

        scene3DOnly: true,
        requestRenderMode: false,
        shadows: true
    });

    viewer.scene.globe.enableLighting = true;
    viewer.scene.globe.depthTestAgainstTerrain = false;

    viewer.scene.screenSpaceCameraController.enableCollisionDetection = true;

    viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(
            LON, LAT, 1800
        ),
        orientation: {
            heading: 0,
            pitch: Cesium.Math.toRadians(-65),
            roll: 0
        },
        duration: 2
    });

    // Load real 3D terrain when an ion token is configured.
    if (TOKEN) {
        try {
            viewer.scene.setTerrain(
                await Cesium.Terrain.fromWorldTerrain()
            );
        } catch (error) {
            showError("3D terrain unavailable. Check your Cesium token.");
        }

        // Load real-world 3D building tiles.
        try {
            const buildings = await Cesium.createOsmBuildingsAsync();

            viewer.scene.primitives.add(buildings);

            document.getElementById("map-status").innerText =
                "AEGIS · SATELLITE + 3D BUILDINGS";

        } catch (error) {
            showError("3D buildings could not load. Check ion access.");
        }

    } else {
        showError(
            "Add CESIUM_ION_TOKEN to enable 3D terrain and buildings."
        );
    }

    // Field center marker.
    viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(LON, LAT),
        point: {
            pixelSize: 12,
            color: Cesium.Color.LIME,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 2,
            heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
        },
        label: {
            text: "AEGIS FIELD",
            font: "bold 13px sans-serif",
            fillColor: Cesium.Color.WHITE,
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 3,
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            pixelOffset: new Cesium.Cartesian2(0, -25)
        }
    });

    // Draw saved field boundary.
    if (
        POLYGON &&
        POLYGON.type === "Feature" &&
        POLYGON.geometry &&
        POLYGON.geometry.coordinates
    ) {
        const positions = [];

        POLYGON.geometry.coordinates[0].forEach(point => {
            positions.push(point[0], point[1]);
        });

        viewer.entities.add({
            polygon: {
                hierarchy: Cesium.Cartesian3.fromDegreesArray(positions),
                material: Cesium.Color.LIME.withAlpha(0.20),
                outline: true,
                outlineColor: Cesium.Color.LIME,
                heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
            }
        });
    }

    // Terrain and imagery are separate layers.
    // Imagery source: Esri World Imagery.
    // 3D buildings source: Cesium ion OpenStreetMap Buildings.

})();
</script>

</body>
</html>
"""

    html = (
        html
        .replace("__TOKEN__", safe_token)
        .replace("__LAT__", safe_lat)
        .replace("__LON__", safe_lon)
        .replace("__POLYGON__", safe_polygon)
    )

    components.html(
        html,
        height=650,
        scrolling=False
    )


# -------------------- HEADER -------------------------------

st.markdown("""
<div class="aegis-header">

    <div>
        <div class="section-label">
            AGRICULTURAL INTELLIGENCE SYSTEM
        </div>

        <div class="aegis-brand">
            AEGIS<span> 2.0</span>
        </div>

        <div class="aegis-subtitle">
            FIELD MONITORING · SATELLITE ANALYTICS · SMART IRRIGATION
        </div>
    </div>

    <div class="aegis-status">
        ● SYSTEM ONLINE
    </div>

</div>
""", unsafe_allow_html=True)


# -------------------- SIDEBAR -------------------------------

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">AEGIS 2.0</div>',
        unsafe_allow_html=True
    )

    st.caption("FIELD CONTROL CENTER")

    st.divider()

    st.subheader("📍 تحديد الموقع")

    place_text = st.text_input(
        "المدينة أو القرية",
        value=st.session_state.place_label
    )

    if st.button("🔎 البحث عن موقع", use_container_width=True):

        try:

            results = geocode(place_text.strip())

            if results:
                st.session_state.location_choices = results
            else:
                st.warning("لم يتم العثور على الموقع.")

        except requests.RequestException as error:
            st.error(f"خطأ تحديد الموقع: {error}")

    choices = st.session_state.location_choices

    if choices:

        selected = st.selectbox(
            "نتائج البحث",
            choices,
            format_func=lambda x:
                f"{x['name']} — {x.get('admin1','')} {x.get('country','')}"
        )

        if st.button("اعتماد الموقع", use_container_width=True):

            st.session_state.lat = float(selected["latitude"])
            st.session_state.lon = float(selected["longitude"])

            st.session_state.place_label = (
                f"{selected['name']}, {selected.get('country','')}"
            )

            st.rerun()

    st.divider()

    st.subheader("🌐 إحداثيات الحقل")

    lat = st.number_input(
        "Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=float(st.session_state.lat),
        format="%.6f"
    )

    lon = st.number_input(
        "Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=float(st.session_state.lon),
        format="%.6f"
    )

    st.session_state.lat = lat
    st.session_state.lon = lon

    st.divider()

    st.subheader("🌱 إعدادات المحصول")

    crop = st.selectbox(
        "المحصول",
        list(CROPS.keys())
    )

    stage = st.selectbox(
        "مرحلة النمو",
        list(STAGES.keys()),
        index=2
    )

    field_area = st.number_input(
        "مساحة الأرض (هكتار)",
        min_value=0.01,
        max_value=100000.0,
        value=float(st.session_state.field_area),
        step=0.1
    )

    st.session_state.field_area = field_area

    efficiency = st.slider(
        "كفاءة نظام الري (%)",
        min_value=40,
        max_value=100,
        value=85
    ) / 100

    soil_awc = st.number_input(
        "السعة المائية المتاحة للتربة (مم/متر)",
        min_value=30,
        max_value=250,
        value=140
    )

    st.divider()

    st.subheader("🛰️ Satellite Engine")

    if CESIUM_TOKEN:
        st.success("Cesium ion token configured")
    else:
        st.warning(
            "3D buildings and terrain require a Cesium ion token."
        )

    if st.button("🔄 تحديث جميع البيانات", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# -------------------- MAIN DATA LOAD ------------------------

lat = float(st.session_state.lat)
lon = float(st.session_state.lon)

try:

    with st.spinner("Connecting to AEGIS data services..."):

        weather = get_weather(lat, lon)

        current = weather.get("current", {})
        daily = weather.get("daily", {})

        end_day = date.today() - timedelta(days=2)
        start_day = end_day - timedelta(days=29)

        nasa = get_nasa_power(
            lat,
            lon,
            start_day.strftime("%Y%m%d"),
            end_day.strftime("%Y%m%d")
        )

    # -------------------- PROCESS WEATHER --------------------

    current_temp = safe_float(
        current.get("temperature_2m")
    )

    current_humidity = safe_float(
        current.get("relative_humidity_2m")
    )

    current_rain = safe_float(
        current.get("precipitation")
    )

    current_wind = safe_float(
        current.get("wind_speed_10m")
    )

    forecast = pd.DataFrame({
        "التاريخ": pd.to_datetime(daily.get("time", [])),
        "العظمى °م": daily.get("temperature_2m_max", []),
        "الصغرى °م": daily.get("temperature_2m_min", []),
        "الأمطار مم": daily.get("precipitation_sum", []),
        "ET₀ مم/يوم": daily.get("et0_fao_evapotranspiration", []),
        "احتمال المطر %": daily.get(
            "precipitation_probability_max",
            [None] * len(daily.get("time", []))
        )
    })

    # -------------------- IRRIGATION MODEL -------------------

    crop_data = CROPS[crop]

    kc = crop_data["kc"] * STAGES[stage]

    et0_values = daily.get(
        "et0_fao_evapotranspiration", []
    )[:3]

    rain_values = daily.get(
        "precipitation_sum", []
    )[:3]

    valid_et0 = [
        float(v) for v in et0_values
        if safe_float(v) is not None
    ]

    valid_rain = [
        float(v) for v in rain_values
        if safe_float(v) is not None
    ]

    et0_3day = (
        sum(valid_et0) / len(valid_et0)
        if valid_et0 else 0
    )

    rain_3day = (
        sum(valid_rain) / len(valid_rain)
        if valid_rain else 0
    )

    etc = et0_3day * kc

    # Average daily effective rain for the planning window.
    effective_rain = (rain_3day / 3) * 0.80

    net_mm = max(
        0,
        etc - effective_rain
    )

    gross_mm = (
        net_mm / efficiency
        if efficiency > 0 else 0
    )

    gross_m3_ha = gross_mm * 10

    gross_field_m3 = gross_m3_ha * field_area

    available_water = (
        crop_data["root"] *
        soil_awc *
        crop_data["depletion"]
    )

    days_between = max(
        1,
        min(
            7,
            int(available_water / max(etc, 0.1))
        )
    )

    # -------------------- TOP METRICS ------------------------

    st.markdown(
        '<div class="section-label">LIVE FIELD OVERVIEW</div>',
        unsafe_allow_html=True
    )

    st.subheader("نظرة عامة على الحقل")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "درجة الحرارة",
        f"{current_temp:.1f} °C"
        if current_temp is not None else "—"
    )

    m2.metric(
        "الرطوبة الجوية",
        f"{current_humidity:.0f}%"
        if current_humidity is not None else "—"
    )

    m3.metric(
        "الأمطار الحالية",
        f"{current_rain:.1f} mm"
        if current_rain is not None else "—"
    )

    m4.metric(
        "سرعة الرياح",
        f"{current_wind:.1f} m/s"
        if current_wind is not None else "—"
    )

    st.caption(
        f"الموقع: {st.session_state.place_label} | "
        f"الإحداثيات: {lat:.5f}, {lon:.5f} | "
        f"التوقيت: {weather.get('timezone', '—')}"
    )

    st.divider()

    # -------------------- NAVIGATION -------------------------

    tab_overview, tab_map, tab_irrigation, tab_climate = st.tabs([
        "◈ Overview",
        "◉ Satellite & 3D Map",
        "◈ Irrigation Intelligence",
        "◈ Climate Analytics"
    ])

    # ========================================================
    # OVERVIEW TAB
    # ========================================================

    with tab_overview:

        st.subheader("تحليل الحالة الجوية")

        left, right = st.columns([1.4, 1])

        with left:

            st.markdown("#### توقعات الطقس — 7 أيام")

            st.dataframe(
                forecast,
                use_container_width=True,
                hide_index=True
            )

        with right:

            st.markdown("#### التغير الحراري")

            if not forecast.empty:

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=forecast["التاريخ"],
                    y=forecast["العظمى °م"],
                    name="Maximum",
                    mode="lines+markers",
                    line=dict(color="#75e5a1", width=3),
                    fill="tozeroy",
                    fillcolor="rgba(117,229,161,.08)"
                ))

                fig.add_trace(go.Scatter(
                    x=forecast["التاريخ"],
                    y=forecast["الصغرى °م"],
                    name="Minimum",
                    mode="lines+markers",
                    line=dict(color="#62a9ee", width=3)
                ))

                fig.update_layout(
                    template="plotly_dark",
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10,r=10,t=20,b=10),
                    legend=dict(orientation="h")
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        st.divider()

        st.subheader("مؤشرات الري الأساسية")

        a, b, c, d = st.columns(4)

        a.metric("ET₀", f"{et0_3day:.2f} mm/day")
        b.metric("ETc", f"{etc:.2f} mm/day")
        c.metric("Kc المستخدم", f"{kc:.2f}")
        d.metric("فاصل الري النظري", f"{days_between} يوم")

        st.info(
            "هذه المؤشرات تقديرية وتعتمد على بيانات الطقس "
            "ومعاملات المحصول. لا تمثل قياسًا مباشرًا للتربة."
        )

    # ========================================================
    # SATELLITE + 3D MAP TAB
    # ========================================================

    with tab_map:

        st.subheader("Geospatial Intelligence Center")

        st.caption(
            "اختر وضع العرض لمراقبة الحقل باستخدام صور الأقمار "
            "الصناعية أو الكرة الأرضية ثلاثية الأبعاد."
        )

        map_mode = st.radio(
            "Map Rendering Mode",
            ["2D Satellite", "3D Earth"],
            horizontal=True,
            label_visibility="collapsed"
        )

        st.markdown(
            '<div class="section-label">LIVE GEOSPATIAL VIEW</div>',
            unsafe_allow_html=True
        )

        if map_mode == "2D Satellite":

            satellite = render_satellite_map(
                lat,
                lon,
                st.session_state.field_polygon
            )

            map_result = st_folium(
                satellite,
                height=650,
                use_container_width=True,
                returned_objects=[
                    "last_clicked",
                    "last_active_drawing"
                ],
                key="aegis_satellite_map"
            )

            # Update field coordinates from map clicks.
            if (
                map_result
                and map_result.get("last_clicked")
            ):

                clicked = map_result["last_clicked"]

                new_lat = float(clicked["lat"])
                new_lon = float(clicked["lng"])

                if (
                    abs(new_lat - lat) > 0.00001
                    or abs(new_lon - lon) > 0.00001
                ):

                    st.session_state.lat = new_lat
                    st.session_state.lon = new_lon

                    st.rerun()

            # Save drawn boundary.
            if (
                map_result
                and map_result.get("last_active_drawing")
            ):

                drawing = map_result["last_active_drawing"]

                if drawing.get("geometry", {}).get("type") == "Polygon":

                    st.session_state.field_polygon = drawing

                    try:
                        measured_area = polygon_area_ha(drawing)

                        st.session_state.field_area = measured_area

                        st.success(
                            f"تم تحديد حدود الأرض. "
                            f"المساحة المقاسة: {measured_area:.3f} هكتار"
                        )

                    except Exception as error:
                        st.warning(f"تعذر حساب المساحة: {error}")

                    st.rerun()

            st.caption(
                "يمكنك رسم حدود الحقل باستخدام أداة Polygon، "
                "أو النقر لتغيير موقع مركز الحقل."
            )

        else:

            render_3d_map(
                lat,
                lon,
                CESIUM_TOKEN,
                st.session_state.field_polygon
            )

            st.caption(
                "استخدم الماوس للدوران والتكبير والميل. "
                "بيانات المباني والتضاريس تعتمد على تغطية Cesium ion."
            )

        st.divider()

        st.subheader("بيانات الحقل الجغرافية")

        g1, g2, g3 = st.columns(3)

        g1.metric("Latitude", f"{lat:.6f}")
        g2.metric("Longitude", f"{lon:.6f}")
        g3.metric(
            "Field Area",
            f"{st.session_state.field_area:.3f} ha"
        )

        if st.session_state.field_polygon:

            st.download_button(
                "تنزيل حدود الحقل GeoJSON",
                data=json.dumps(
                    st.session_state.field_polygon,
                    ensure_ascii=False
                ),
                file_name="aegis_field_boundary.geojson",
                mime="application/geo+json"
            )

    # ========================================================
    # IRRIGATION INTELLIGENCE TAB
    # ========================================================

    with tab_irrigation:

        st.subheader("Smart Irrigation Intelligence")

        st.info(
            "يعتمد الحساب على ET₀ المتوقع ومعامل المحصول "
            "ومرحلة النمو والأمطار وكفاءة نظام الري."
        )

        i1, i2, i3, i4 = st.columns(4)

        i1.metric("Reference ET₀", f"{et0_3day:.2f} mm/day")
        i2.metric("Crop ETc", f"{etc:.2f} mm/day")
        i3.metric("Net Irrigation", f"{net_mm:.2f} mm/day")
        i4.metric("Gross Irrigation", f"{gross_mm:.2f} mm/day")

        st.divider()

        st.subheader("حجم المياه المطلوب")

        q1, q2 = st.columns(2)

        q1.metric(
            "المياه لكل هكتار",
            f"{gross_m3_ha:.2f} m³/day"
        )

        q2.metric(
            "المياه للحقل بالكامل",
            f"{gross_field_m3:.2f} m³/day"
        )

        st.divider()

        st.subheader("تفاصيل معادلة الحساب")

        formula = pd.DataFrame({
            "المتغير": [
                "ET₀",
                "Kc",
                "ETc",
                "Effective Rain",
                "Net Irrigation",
                "System Efficiency",
                "Gross Irrigation",
            ],
            "القيمة": [
                round(et0_3day, 3),
                round(kc, 3),
                round(etc, 3),
                round(effective_rain, 3),
                round(net_mm, 3),
                f"{efficiency * 100:.0f}%",
                round(gross_mm, 3),
            ]
        })

        st.dataframe(
            formula,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### نموذج احتياج المياه")

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=["ETc", "Net irrigation", "Gross irrigation"],
            y=[etc, net_mm, gross_mm],
            text=[
                f"{etc:.2f}",
                f"{net_mm:.2f}",
                f"{gross_mm:.2f}"
            ],
            textposition="outside",
            marker_color=["#75e5a1", "#62a9ee", "#d5b46a"]
        ))

        fig.update_layout(
            template="plotly_dark",
            height=370,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis_title="mm/day"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.warning(
            f"فاصل الري النظري: {days_between} يوم. "
            "يجب التحقق من رطوبة منطقة الجذور والمطر الفعلي "
            "قبل اعتماد موعد الري."
        )

    # ========================================================
    # CLIMATE ANALYTICS TAB
    # ========================================================

    with tab_climate:

        st.subheader("NASA POWER Climate Analytics")

        historical = nasa_frame(nasa)

        names = {
            "T2M": "متوسط الحرارة °م",
            "T2M_MAX": "العظمى °م",
            "T2M_MIN": "الصغرى °م",
            "PRECTOTCORR": "الأمطار مم/يوم",
            "RH2M": "الرطوبة %",
            "ALLSKY_SFC_SW_DWN": "الإشعاع الشمسي kWh/m²/day",
        }

        historical = historical.rename(columns=names)

        st.caption(
            "بيانات من شبكة NASA POWER المناخية اليومية. "
            "ليست قراءة مباشرة من محطة داخل الحقل."
        )

        if not historical.empty:

            available = [
                name for name in [
                    "متوسط الحرارة °م",
                    "العظمى °م",
                    "الصغرى °م"
                ]
                if name in historical.columns
            ]

            if available:

                st.markdown("#### Historical Temperature")

                fig = px.line(
                    historical,
                    y=available,
                    template="plotly_dark",
                    markers=True
                )

                fig.update_layout(
                    height=380,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            if "الأمطار مم/يوم" in historical.columns:

                st.markdown("#### Historical Rainfall")

                rain_fig = px.bar(
                    historical,
                    y="الأمطار مم/يوم",
                    template="plotly_dark"
                )

                rain_fig.update_layout(
                    height=320,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(
                    rain_fig,
                    use_container_width=True
                )

            st.markdown("#### Historical Data Table")

            st.dataframe(
                historical.tail(30).round(2),
                use_container_width=True
            )

            st.download_button(
                "⬇ Download NASA POWER CSV",
                data=historical.to_csv(
                    index_label="date"
                ).encode("utf-8-sig"),
                file_name="aegis_climate_history.csv",
                mime="text/csv"
            )

        else:
            st.warning("لا توجد بيانات تاريخية متاحة.")

    # -------------------- FOOTER -----------------------------

    st.divider()

    st.markdown("""
    <div style="
        display:flex;
        justify-content:space-between;
        flex-wrap:wrap;
        gap:12px;
        color:#81978b;
        font-size:11px;
    ">
        <span>AEGIS 2.0 · AGRICULTURAL INTELLIGENCE</span>
        <span>OPEN-METEO · NASA POWER · ESRI · CESIUM</span>
    </div>
    """, unsafe_allow_html=True)

except requests.RequestException as error:

    st.error(f"External data connection failed: {error}")

    st.info(
        "تحقق من اتصال الإنترنت ومصادر البيانات "
        "ثم حاول تحديث التطبيق."
    )

except (ValueError, KeyError, TypeError, ZeroDivisionError) as error:

    st.error(f"Data processing error: {error}")

    st.info(
        "راجع البيانات المستلمة وإعدادات الحقل."
    )