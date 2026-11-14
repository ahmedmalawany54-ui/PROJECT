# Field Shift | AEGIS Smart Farming

A prototype dashboard combining NASA POWER historical weather observations,
crop-stage rule checks, soil-moisture sensor readings, and an interactive field-aware AEGIS advisor.

## Project files

- `app.py`: Streamlit dashboard and interactive map.
- `nasa_api.py`: NASA POWER API client, validation, retries, and data cleaning.
- `crop_intelligence.py`: crop/stage rule engine.
- `advisor_engine.py`: context-aware AEGIS advisor that explains current field readings and recommendations.
- `sensor_receiver.py`: optional FastAPI gateway for ESP32 readings.
- `esp32_sensor_example.ino`: ESP32 example for a capacitive soil-moisture sensor.
- `requirements.txt`: Python dependencies.

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Sensor integration (optional)

Run the sensor gateway in a second terminal:

```bash
uvicorn sensor_receiver:app --host 0.0.0.0 --port 8000
```

Test it:

```bash
curl -X POST http://localhost:8000/sensor \
  -H "Content-Type: application/json" \
  -d '{"device_id":"field-01","soil_moisture":38.5}'
```

In the dashboard, select `بوابة ESP32 / API`, use `http://localhost:8000`,
and fetch the latest reading. For an ESP32 on another device, use the host
computer's LAN IP instead of localhost.

## Important scientific and deployment limitations

1. NASA POWER variables used here are T2M (air temperature at 2 m),
   RH2M (relative humidity at 2 m), and PRECTOTCORR (corrected precipitation).
   They are historical gridded products, not real-time field sensors or forecasts.
2. Relative humidity is not soil moisture. The dashboard keeps these separate.
3. Crop thresholds are illustrative starting values, not validated prescriptions.
   Confirm cultivar, soil texture, irrigation method, local climate, and growth-stage
   requirements with local agronomic expertise.
4. Soil sensor percentage must be calibrated for the exact probe and soil.
   The ESP32 sample's raw calibration values are placeholders.
5. The current risk engine is transparent rule-based decision support, not a trained
   machine-learning model and not a disease diagnosis.
6. The AEGIS advisor in this release is a deterministic, explainable question-answer layer over the current field data; it is not a generative LLM and does not invent missing measurements.
7. The optional sensor gateway is a prototype. Do not expose it to the public internet
   without authentication, HTTPS, access control, rate limiting, and persistent storage.
8. The sensor gateway stores only the latest reading in a local JSON file; it is not
   a historical sensor database.

## Suggested next production steps

- Calibrate crop profiles with local agronomists and field trials.
- Store time-stamped sensor readings in a database.
- Add authenticated devices and HTTPS.
- Integrate a forecast provider separately from NASA historical observations.
- Evaluate recommendations against measured soil water, evapotranspiration,
  crop coefficients, and irrigation system characteristics.
