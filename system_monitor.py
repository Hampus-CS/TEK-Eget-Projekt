import os
import sqlite3
import psutil
import GPUtil
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Ladda miljövariabler från .env-filen
load_dotenv()

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_ram_usage():
    memory = psutil.virtual_memory()
    return memory.percent

def get_gpu_usage():
    gpus = GPUtil.getGPUs()
    gpu_usages = {}
    for gpu in gpus:
        gpu_usages[gpu.id] = gpu.load * 100
    return gpu_usages

def get_co2_intensity(zone="SE"):
    # Hämta autentiseringsuppgifter från miljövariabler
    email = os.getenv("ELECTRICITY_MAPS_EMAIL")
    api_key = os.getenv("ELECTRICITY_MAPS_API_KEY")
    
    url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone}"
    headers = {
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, auth=HTTPBasicAuth(email, api_key))
        response.raise_for_status()
        data = response.json()
        # Justera nyckeln nedan utifrån API-svaret
        co2_intensity = data.get('carbonIntensity')
        return co2_intensity
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def init_db(db_path="energy_data.db"):
    """Skapar och initierar SQLite-databasen om den inte redan finns."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_usage REAL,
            ram_usage REAL,
            gpu_usage REAL,
            co2_intensity REAL
        )
    """)
    conn.commit()
    return conn

def save_data_to_db(conn, cpu_usage, ram_usage, gpu_usage, co2_intensity):
    """Sparar insamlade data i SQLite-databasen."""
    cursor = conn.cursor()
    # För GPU-värdet väljer vi första värdet (eller 0.0 om inga hittades)
    gpu_val = next(iter(gpu_usage.values()), 0.0) if gpu_usage else 0.0
    cursor.execute("""
        INSERT INTO system_data (cpu_usage, ram_usage, gpu_usage, co2_intensity)
        VALUES (?, ?, ?, ?)
    """, (cpu_usage, ram_usage, gpu_val, co2_intensity))
    conn.commit()

if __name__ == "__main__":
    cpu_usage = get_cpu_usage()
    ram_usage = get_ram_usage()
    gpu_usage = get_gpu_usage()
    
    print(f"CPU-användning: {cpu_usage}%")
    print(f"RAM-användning: {ram_usage}%")
    
    if gpu_usage:
        print("GPU-användning:")
        for gpu_id, usage in gpu_usage.items():
            print(f"  GPU {gpu_id}: {usage}%")
    else:
        print("Inga GPU:er hittades eller ingen GPU-data tillgänglig.")
    
    co2_intensity = get_co2_intensity()
    if co2_intensity is not None:
        print(f"CO₂-intensitet: {co2_intensity}")
    else:
        print("Kunde inte hämta CO₂-intensitet från Electricity Maps.")
    
    # Initiera SQLite-databasen och spara data
    conn = init_db()
    save_data_to_db(conn, cpu_usage, ram_usage, gpu_usage, co2_intensity)
    conn.close()
    print("Data sparad i SQLite-databasen 'energy_data.db'.")
