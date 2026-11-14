"""Vegetation check: is there green cover at the selected point?

Source: MODIS 16-day NDVI (250 m) through the NASA ORNL DAAC TESViS web service
(no API key needed). NDVI shows how green the area is, not which crop is growing.
"""
import statistics
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

BASE = "https://modis.ornl.gov/rst/api/v1"
PRODUCTS = ("MOD13Q1", "MYD13Q1")  # Terra, then Aqua as a fallback
HEADERS = {"Accept": "application/json"}
SCALE = 0.0001  # MODIS NDVI scale factor
VALID_MIN = -2000  # raw values below this are fill/no-data (-3000)


def classify(ndvi):
    if ndvi < 0.12:
        return "barren"
    if ndvi < 0.20:
        return "sparse"
    if ndvi < 0.40:
        return "moderate"
    return "dense"


def _to_date(modis_code):  # "A2018049" -> 2018-02-18
    return datetime.strptime(modis_code[1:], "%Y%j")


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def get_vegetation(lat, lng, n_dates=10, km=1):
    """Median NDVI of cloud-free pixels around the point for the last `n_dates` composites."""
    last_error = "No data returned."
    for product in PRODUCTS:
        try:
            r = requests.get(f"{BASE}/{product}/dates",
                             params={"latitude": lat, "longitude": lng},
                             headers=HEADERS, timeout=(5, 30))
            r.raise_for_status()
            payload = r.json()
            items = payload.get("dates", []) if isinstance(payload, dict) else payload
            dates = sorted(d["modis_date"] if isinstance(d, dict) else d for d in items)
            if not dates:
                last_error = f"{product}: no composite dates for this point (maybe ocean)."
                continue
            dates = dates[-n_dates:]

            r = requests.get(f"{BASE}/{product}/subset",
                             params={"latitude": lat, "longitude": lng,
                                     "startDate": dates[0], "endDate": dates[-1],
                                     "kmAboveBelow": km, "kmLeftRight": km},
                             headers=HEADERS, timeout=(5, 60))
            r.raise_for_status()
            subset = r.json()["subset"]
            ndvi = {s["modis_date"]: s["data"] for s in subset if s["band"].endswith("_NDVI")}
            quality = {s["modis_date"]: s["data"] for s in subset if s["band"].endswith("pixel_reliability")}

            points = {}
            for code, values in ndvi.items():
                flags = quality.get(code) or [0] * len(values)
                good = [v * SCALE for v, q in zip(values, flags) if v > VALID_MIN and q in (0, 1)]
                if good:
                    points[_to_date(code)] = statistics.median(good)
            if not points:
                last_error = f"{product}: only cloudy/invalid pixels in recent composites."
                continue

            series = pd.Series(points).sort_index()
            latest = float(series.iloc[-1])
            return {"status": "success", "series": series, "latest": latest,
                    "date": series.index[-1].strftime("%Y-%m-%d"),
                    "level": classify(latest), "product": product}
        except requests.exceptions.Timeout:
            last_error = f"{product}: request timed out."
        except requests.exceptions.RequestException as exc:
            last_error = f"{product}: network/API error ({exc.__class__.__name__})."
        except (KeyError, ValueError, TypeError) as exc:
            last_error = f"{product}: unexpected response ({exc.__class__.__name__})."
    return {"status": "error", "message": last_error}