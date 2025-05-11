# TEK-Eget-Projekt

This project monitors system resource usage (CPU, RAM, GPU) and fetches the latest CO₂ intensity data from the Electricity Map API for “Södra Mellansverige” (SE-SE3). It is built in Python, stores data locally in SQLite, and serves a lightweight web UI via Flask.

## Table of Contents

- [Features](#features)  
- [Requirements](#requirements)  
- [Installation](#installation)  
  - [Without Virtual Environment](#without-virtual-environment)  
  - [With Virtual Environment](#with-virtual-environment)  
- [Usage](#usage)  
- [Configuration](#configuration)  
- [Troubleshooting](#troubleshooting)  
- [Project Structure](#project-structure)  
- [License](#license)  

## Features

- **System Monitoring**: Retrieves CPU, RAM, and GPU usage every minute.  
- **CO₂ Intensity**: Fetches carbon intensity (g/kWh) for SE-SE3 max once per hour.  
- **Local Storage**: Saves all data in a local SQLite database (`energy_data.db`).  
- **Web UI**: Displays latest values and 60-minute history graph, with auto-refresh.  
- **Lightweight**: No external database service required; pure file-based.

## Requirements

- **Python 3.8+**  
- **pip** (Python package installer)  

## Installation

### Without Virtual Environment

1. **Clone repository**  
   ```bash
   git clone https://github.com/yourusername/TEK-Eget-Projekt.git
   cd TEK-Eget-Projekt
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

### With Virtual Environment

1. **Clone repository**  
   ```bash
   git clone https://github.com/yourusername/TEK-Eget-Projekt.git
   cd TEK-Eget-Projekt
   ```

2. **Create and activate venv**  
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Create `.env`** in project root. Example:

   ```ini
   ELECTRICITY_MAPS_EMAIL=hampus.carlstromsvanberg@elev.ga.lbs.se
   ELECTRICITY_MAPS_API_KEY=RGQHkCL45UnqR6ctU8rW
   ZONE=SE-SE3
   HOST=127.0.0.1
   PORT=5000
   MONITOR_INTERVAL=60
   DB_PATH=energy_data.db
   ```

   - `ELECTRICITY_MAPS_EMAIL` and `ELECTRICITY_MAPS_API_KEY` are your credentials for the Electricity Map API.  
   - **Do not** commit this file to version control; it is included in `.gitignore`.

2. **Run all components** (Windows):  
   - Double-click `run.bat`  
     - activates venv  
     - starts Flask API/UI (`api_ui.py`)  
     - starts monitor (`system_monitor.py`)  
     - opens browser at `http://127.0.0.1:5000`

   **Or manually**:  
   ```bash
   python api_ui.py
   python system_monitor.py
   ```

3. **View in browser**  
   Open `http://127.0.0.1:5000` to see live data.

## Configuration

Configure the behavior of the application by setting environment variables in your `.env` file:

- **ELECTRICITY_MAPS_EMAIL**: Your Electricity Map account email (used for authentication).  
- **ELECTRICITY_MAPS_API_KEY**: Your Electricity Map API token (used for authentication).  
- **ZONE**: Electricity Map zone to fetch CO₂ intensity for (default `SE-SE3` for Södra Mellansverige).  
- **HOST**: Host address for the Flask server (default `127.0.0.1`).  
- **PORT**: Port number for the Flask server (default `5000`).  
- **MONITOR_INTERVAL**: Interval in seconds between each system measurement (default `60`).  
- **DB_PATH**: Path to the local SQLite database file (default `energy_data.db`).

(do **not** commit this file to version control)

## Troubleshooting

- **401 Unauthorized**: Check your API credentials in `.env`.  
- **Empty UI**: Run `system_monitor.py` at least once, then reload page.  
- **Dependency Errors**:  
  ```bash
  pip install -r requirements.txt
  ```
- **Port Conflicts**: Modify `PORT` in `.env` if 5000 is in use.

## Project Structure

```
TEK-Eget-Projekt/
├── api_ui.py            # Flask app + API endpoints + web UI
├── system_monitor.py    # Collects metrics & CO₂ data, writes to SQLite
├── index.html           # Jinja2 template for UI (in project root)
├── run.bat              # Windows batch to start everything
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
├── .gitignore           # Excludes venv, .env, .db, etc.
├── README.md            # This file
└── energy_data.db       # Local SQLite (auto-created)
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
