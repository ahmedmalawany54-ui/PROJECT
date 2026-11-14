"""Crop data (Kc by stage) and indicative soil-test ranges.

NPK ranges are rough, general guidance in mg/kg. Always validate against a
soil laboratory and local agronomy recommendations.
"""

STAGES = ("init", "mid", "late")  # index into the Kc tuple

CROPS = {
    "wheat":  {"ar": "قمح",    "en": "Wheat",  "kc": (0.30, 1.15, 0.25),
               "ph": (6.0, 7.8), "n": (20, 50), "p": (10, 25), "k": (120, 250)},
    "maize":  {"ar": "ذرة",    "en": "Maize",  "kc": (0.30, 1.20, 0.60),
               "ph": (5.8, 7.5), "n": (25, 60), "p": (10, 30), "k": (130, 250)},
    "tomato": {"ar": "طماطم",  "en": "Tomato", "kc": (0.60, 1.15, 0.80),
               "ph": (6.0, 7.0), "n": (30, 60), "p": (15, 35), "k": (150, 300)},
    "cotton": {"ar": "قطن",    "en": "Cotton", "kc": (0.35, 1.15, 0.70),
               "ph": (6.0, 8.0), "n": (20, 50), "p": (10, 25), "k": (120, 250)},
    "clover": {"ar": "برسيم",  "en": "Clover (Berseem)", "kc": (0.40, 1.05, 0.90),
               "ph": (6.0, 7.8), "n": (10, 30), "p": (10, 30), "k": (120, 250)},
}


def kc_for(crop, stage):
    return CROPS[crop]["kc"][STAGES.index(stage)]


def assess_soil(crop, n, p, k, ph):
    """Compare readings with the crop's indicative range.

    Returns a list of dicts: key, value, low, high, status ('low' | 'ok' | 'high').
    """
    c = CROPS[crop]
    rows = []
    for key, value in (("n", n), ("p", p), ("k", k), ("ph", ph)):
        low, high = c[key]
        status = "low" if value < low else "high" if value > high else "ok"
        rows.append({"key": key, "value": value, "low": low, "high": high, "status": status})
    return rows