import psutil
import GPUtil
import requests
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load environment variables from .env file
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
    # Load authentication credentials from environment variables
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
        # Adjust key extraction as needed based on API response structure.
        co2_intensity = data.get('carbonIntensity')
        return co2_intensity
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

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
