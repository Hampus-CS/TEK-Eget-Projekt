import os
import sqlite3
import psutil
import GPUtil
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# --- Ladda .env ---
load_dotenv()

# --- Konfiguration ---
DB_PATH      = os.getenv("DB_PATH", "energy_data.db")
ZONE         = os.getenv("ZONE",    "SE-SE3")
API_KEY      = os.getenv("ELECTRICITY_MAPS_API_KEY")
INTERVAL     = int(os.getenv("MONITOR_INTERVAL",  60))  # s mellan mätningar
HISTORY_MIN  = 60    # behåll 60 minuters historik
CO2_INTERVAL = 3600  # hämta CO₂-intensitet max var timme

# --- Databasanslutning & initiering ---
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn):
    cur = conn.cursor()
    # Settings-tabell
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    for k, v in [("CPU_TDP","65"), ("GPU_TDP","180")]:
        cur.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)",
            (k, v)
        )
    # System_data-tabell
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

# --- Läs TDP-värden ---
def get_tdps(conn):
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key='CPU_TDP'")
    cpu = float(cur.fetchone()["value"])
    cur.execute("SELECT value FROM settings WHERE key='GPU_TDP'")
    gpu = float(cur.fetchone()["value"])
    return cpu, gpu

# --- Mätfunktioner ---
def get_cpu():
    return psutil.cpu_percent(interval=1)

def get_ram():
    return psutil.virtual_memory().percent

def get_gpu():
    gpus = GPUtil.getGPUs()
    return next((gpu.load * 100 for gpu in gpus), 0.0)

# --- Hämta CO₂-intensitet ---
def fetch_co2(zone=ZONE):
    url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone}"
    headers = {
        "Accept":     "application/json",
        "auth-token": API_KEY
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("carbonIntensity")

# --- Beräkna CO₂-utsläpp ---
def calc_co2(cpu_pct, gpu_pct, cpu_tdp, gpu_tdp, intensity, secs):
    power = cpu_tdp * (cpu_pct / 100.0) + gpu_tdp * (gpu_pct / 100.0)  # watt
    kwh   = power * secs / 3_600_000                                 # kWh
    return kwh * intensity                                           # gram CO₂

# --- Spara & trimma historik ---
def save_and_trim(conn, cpu, ram, gpu, intensity, emission):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO system_data (
            cpu_usage, ram_usage, gpu_usage,
            co2_intensity, co2_emission
        ) VALUES (?, ?, ?, ?, ?)
    """, (cpu, ram, gpu, intensity, emission))
    # Ta bort poster äldre än HISTORY_MIN minuter
    cur.execute(f"""
        DELETE FROM system_data
        WHERE timestamp < datetime('now','-{HISTORY_MIN} minutes')
    """)
    conn.commit()

# --- Huvudloop ---
if __name__ == "__main__":
    conn = get_db()
    init_db(conn)

    print(f"[{datetime.now()}] Startar monitor: intervall={INTERVAL}s, CO₂-uppdatering var={CO2_INTERVAL}s, zone={ZONE}")

    last_ts, last_intensity = 0, None

    while True:
        cpu_tdp, gpu_tdp = get_tdps(conn)
        cpu = get_cpu()
        ram = get_ram()
        gpu = get_gpu()

        now = time.time()
        if last_intensity is None or (now - last_ts) >= CO2_INTERVAL:
            try:
                last_intensity = fetch_co2()
                last_ts        = now
                print(f"[{datetime.now()}] Ny CO₂-intensitet ({ZONE}): {last_intensity:.1f} g/kWh")
            except Exception as e:
                print(f"[{datetime.now()}] FEL CO₂-hämtning: {e}")
        else:
            print(f"[{datetime.now()}] Återanvänder CO₂-intensitet: {last_intensity:.1f} g/kWh")

        if last_intensity is not None:
            emission = calc_co2(cpu, gpu, cpu_tdp, gpu_tdp, last_intensity, INTERVAL)
            print(f"[{datetime.now()}] CPU {cpu:.1f}%  RAM {ram:.1f}%  GPU {gpu:.1f}%  CO₂ {emission:.2f} g")
            save_and_trim(conn, cpu, ram, gpu, last_intensity, emission)
        else:
            print(f"[{datetime.now()}] Skippade CO₂-beräkning")

        time.sleep(INTERVAL)
