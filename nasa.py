"""NASA POWER data: history, FAO-56 reference evapotranspiration (ET0), water balance."""
import math
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
import streamlit as st

POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETERS = "T2M,T2M_MAX,T2M_MIN,RH2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN,WS2M"


# ---------- ET0 (FAO-56 Penman-Monteith, daily) ----------
def _sat_vp(t):
    return 0.6108 * math.exp(17.27 * t / (t + 237.3))


def _extraterrestrial_radiation(lat, doy):
    phi = math.radians(lat)
    dr = 1 + 0.033 * math.cos(2 * math.pi * doy / 365)
    decl = 0.409 * math.sin(2 * math.pi * doy / 365 - 1.39)
    x = max(-1.0, min(1.0, -math.tan(phi) * math.tan(decl)))
    ws = math.acos(x)
    return 37.586 * dr * (
        ws * math.sin(phi) * math.sin(decl)
        + math.cos(phi) * math.cos(decl) * math.sin(ws)
    )


def et0_fao56(lat, date, tmax, tmin, rh, rs_mj, u2):
    """Returns ET0 in mm/day. rs_mj = solar radiation in MJ/m2/day, u2 = wind at 2 m (m/s).

    NASA POWER's AG community returns ALLSKY_SFC_SW_DWN in MJ/m2/day already,
    so no unit conversion is needed here.
    """
    tmean = (tmax + tmin) / 2
    rs = rs_mj
    es = (_sat_vp(tmax) + _sat_vp(tmin)) / 2
    ea = es * rh / 100
    delta = 4098 * _sat_vp(tmean) / (tmean + 237.3) ** 2
    gamma = 0.0674  # kPa/C, sea-level approximation
    ra = _extraterrestrial_radiation(lat, date.timetuple().tm_yday)
    rso = 0.75 * ra
    ratio = min(rs / rso, 1.0) if rso > 0 else 0.5
    rns = 0.77 * rs
    rnl = (
        4.903e-9
        * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2)
        * (0.34 - 0.14 * math.sqrt(max(ea, 0)))
        * (1.35 * ratio - 0.35)
    )
    rn = rns - rnl
    num = 0.408 * delta * rn + gamma * 900 / (tmean + 273) * u2 * (es - ea)
    den = delta + gamma * (1 + 0.34 * u2)
    return max(0.0, num / den)


# ---------- NASA POWER ----------
@st.cache_data(ttl=3600, show_spinner=False)
def get_nasa_history(lat, lng, days=21):
    """Daily history ending ~2 days ago (POWER is delayed, not real-time)."""
    end = datetime.now(timezone.utc).date() - timedelta(days=2)
    start = end - timedelta(days=days - 1)
    params = {
        "parameters": PARAMETERS,
        "community": "AG",
        "longitude": float(lng),
        "latitude": float(lat),
        "format": "JSON",
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
    }
    try:
        r = requests.get(POWER_URL, params=params, timeout=(5, 25))
        r.raise_for_status()
        data = r.json()["properties"]["parameter"]
        df = pd.DataFrame(data)
        df.index = pd.to_datetime(df.index, format="%Y%m%d")
        df = df.sort_index()
        df = df.where(df > -900).dropna()
        if df.empty:
            return {"status": "error", "message": "No valid NASA POWER measurements for this period."}
        df["ET0"] = [
            et0_fao56(lat, idx.date(), row["T2M_MAX"], row["T2M_MIN"],
                      row["RH2M"], row["ALLSKY_SFC_SW_DWN"], row["WS2M"])
            for idx, row in df.iterrows()
        ]
        return {"status": "success", "df": df}
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "NASA POWER request timed out."}
    except requests.exceptions.RequestException as exc:
        return {"status": "error", "message": f"Network/API error: {exc}"}
    except (KeyError, ValueError, TypeError) as exc:
        return {"status": "error", "message": f"Unexpected NASA response: {exc}"}


def irrigation_balance(df, kc, window=7):
    """Crop water demand (ETc) minus effective rain over the last `window` days."""
    recent = df.tail(window)
    etc = float((recent["ET0"] * kc).sum())
    eff_rain = float(sum(0.0 if r < 2 else r * 0.8 for r in recent["PRECTOTCORR"]))
    deficit = etc - eff_rain
    if deficit <= 5:
        level = "ok"
    elif deficit <= 20:
        level = "light"
    else:
        level = "irrigate"
    return {"etc": etc, "rain": eff_rain, "deficit": deficit, "level": level, "days": len(recent)}