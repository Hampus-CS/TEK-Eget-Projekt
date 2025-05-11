import os
import sqlite3
import requests
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from dotenv import load_dotenv

# --- Ladda .env ---
load_dotenv()

# --- Konfiguration ---
DB_PATH = os.getenv("DB_PATH", "energy_data.db")
HOST    = os.getenv("HOST",    "127.0.0.1")
PORT    = int(os.getenv("PORT",  "5000"))
ZONE    = os.getenv("ZONE",    "SE-SE3")                # Södra Mellansverige
API_KEY = os.getenv("ELECTRICITY_MAPS_API_KEY")         # Din token

# --- Initiera Flask och peka på templates ---
app = Flask(__name__, template_folder='.')

# --- Initiera databasen (skapa fil + tabeller) ---
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur  = conn.cursor()

    # Inställningar (TDP)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    for key, val in [("CPU_TDP", "65"), ("GPU_TDP", "180")]:
        cur.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, val)
        )

    # Systemdata
    cur.execute("""
        CREATE TABLE IF NOT EXISTS system_data (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp      DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_usage      REAL,
            ram_usage      REAL,
            gpu_usage      REAL,
            co2_intensity  REAL,
            co2_emission   REAL
        )
    """)
    conn.commit()
    conn.close()

# Kör init_db vid varje uppstart
init_db()

# --- Skapa en långlivad anslutning ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn   = get_db_connection()
cursor = conn.cursor()

# --- Hämta aktuell CO₂-intensitet från ElectricityMaps ---
def fetch_co2(zone=ZONE):
    url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone}"
    headers = {
        "Accept":     "application/json",
        "auth-token": API_KEY
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("carbonIntensity")

# --- API: Spara TDP-inställningar ---
@app.route('/api/settings', methods=['POST'])
def save_settings():
    data = request.get_json(force=True)
    cpu = data.get('cpu_tdp')
    gpu = data.get('gpu_tdp')
    if cpu is None or gpu is None:
        return jsonify(error="CPU_TDP och GPU_TDP krävs"), 400

    cursor.execute("UPDATE settings SET value = ? WHERE key = 'CPU_TDP'", (str(cpu),))
    cursor.execute("UPDATE settings SET value = ? WHERE key = 'GPU_TDP'", (str(gpu),))
    conn.commit()
    return jsonify(message="Inställningar uppdaterade"), 200

# --- API: Ta emot och spara systemdata ---
@app.route('/api/data', methods=['POST'])
def save_system_data():
    d   = request.get_json(force=True)
    cpu = d.get('cpu_usage')
    ram = d.get('ram_usage')
    gpu = d.get('gpu_usage')
    ci  = d.get('co2_intensity')
    ce  = d.get('co2_emission')
    if None in (cpu, ram, gpu, ci, ce):
        return jsonify(error="Alla fält krävs"), 400

    cursor.execute("""
        INSERT INTO system_data (
          cpu_usage, ram_usage, gpu_usage,
          co2_intensity, co2_emission
        ) VALUES (?, ?, ?, ?, ?)
    """, (cpu, ram, gpu, ci, ce))
    conn.commit()
    return jsonify(message="Data sparad"), 200

# --- API: Hämta 60-minuters historik ---
@app.route('/api/history', methods=['GET'])
def get_history():
    cursor.execute("""
        SELECT timestamp, cpu_usage, ram_usage, gpu_usage,
               co2_intensity, co2_emission
        FROM system_data
        WHERE timestamp >= datetime('now','-60 minutes')
        ORDER BY timestamp ASC
    """)
    rows = cursor.fetchall()
    history = [
        {
            "timestamp":     row["timestamp"],
            "cpu_usage":     row["cpu_usage"],
            "ram_usage":     row["ram_usage"],
            "gpu_usage":     row["gpu_usage"],
            "co2_intensity": row["co2_intensity"],
            "co2_emission":  row["co2_emission"]
        }
        for row in rows
    ]
    return jsonify(history), 200

# --- Frontend: Rendera index.html ---
@app.route('/')
def index():
    # Hämta senaste dataraden
    cursor.execute("SELECT * FROM system_data ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()

    # Default-data om tabellen är tom
    data = {
        "timestamp":     None,
        "cpu_usage":     0,
        "ram_usage":     0,
        "gpu_usage":     0,
        "co2_intensity": 0,
        "co2_emission":  0
    }
    if row:
        data.update(dict(row))

    # Hämta färsk CO₂-intensitet (överskriver eventuell DB-kopia)
    try:
        data["co2_intensity"] = fetch_co2()
    except Exception:
        pass

    # Läsa in TDP-inställningar för formuläret
    cursor.execute("SELECT value FROM settings WHERE key='CPU_TDP'")
    cpu_tdp = float(cursor.fetchone()[0])
    cursor.execute("SELECT value FROM settings WHERE key='GPU_TDP'")
    gpu_tdp = float(cursor.fetchone()[0])

    return render_template(
        'index.html',
        data=data,
        cpu_tdp=cpu_tdp,
        gpu_tdp=gpu_tdp
    )

# --- Starta Flask ---
if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
