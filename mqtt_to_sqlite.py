from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime

import os
from dotenv import load_dotenv
import google.generativeai as genai


app = Flask(__name__, static_folder="static")
CORS(app)

DB_FILE = "sensor_data.db"

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_latest_readings():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic, value, timestamp
        FROM readings
        WHERE timestamp = (
            SELECT MAX(timestamp)
            FROM readings r2
            WHERE r2.topic = readings.topic
        )
    """)

    rows = cursor.fetchall()
    conn.close()

    data = {
        "temperature": None,
        "humidity": None,
        "soil": None,
        "updated": None,  # keep as datetime for now
    }

    for topic, value, timestamp in rows:
        topic_l = topic.lower()

        if "temp" in topic_l:
            data["temperature"] = float(value)
        elif "hum" in topic_l:
            data["humidity"] = float(value)
        elif "soil" in topic_l or "moist" in topic_l:
            data["soil"] = float(value)

        # Parse timestamp safely
        try:
            ts = datetime.fromisoformat(timestamp)
        except ValueError:
            ts = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

        if data["updated"] is None or ts > data["updated"]:
            data["updated"] = ts

    # Fallbacks
    if data["temperature"] is None:
        data["temperature"] = 0
    if data["humidity"] is None:
        data["humidity"] = 0
    if data["soil"] is None:
        data["soil"] = 0
    if data["updated"] is None:
        data["updated"] = datetime.now()

    # ✅ convert datetime → string ONLY here
    data["updated"] = data["updated"].isoformat()

    return data

def get_history(hours=24):
    """
    Fetch sensor readings from the last N hours.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic, value, timestamp
        FROM readings
        WHERE timestamp >= datetime('now', ?)
        ORDER BY timestamp ASC
    """, (f"-{hours} hours",))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for topic, value, timestamp in rows:
        history.append({
            "topic": topic,
            "value": float(value),
            "timestamp": timestamp
        })

    return history

def predict_next_5_hours(history):
    """
    Uses Gemini to forecast next 5 hours based on sensor history.
    """
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
        You are an environmental forecasting AI for road ice detection.

        The historical data MAY be sparse or limited.
        If trends are unclear, make reasonable assumptions and extrapolate.

        Given the following historical sensor readings (timestamped),
        predict the next 5 hours in 1-hour intervals.

        Return ONLY valid JSON in this format:

        {{
        "forecast": [
            {{
            "hour": "+1h",
            "temperature": number,
            "humidity": number,
            "risk": "LOW|MEDIUM|HIGH"
            }}
        ],
        "summary": "one short sentence"
        }}

        Historical data:
        {history}
        """

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Extract JSON safely
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Gemini returned non-JSON")

    return text[start:end + 1]


@app.route("/api/latest")
def latest():
    return jsonify(get_latest_readings())

@app.route("/api/forecast")
def forecast():
    try:
        history = get_history(hours=24)

        # Even if history is small, let Gemini extrapolate
        prediction_json = predict_next_5_hours(history)

        return app.response_class(
            response=prediction_json,
            mimetype="application/json"
        )

    except Exception as e:
        return jsonify({
            "error": "Prediction failed",
            "details": str(e)
        }), 500



# Serve frontend
@app.route("/")
def index():
    return send_from_directory("frontend", "iot.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
