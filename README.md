# TEK-Eget-Projekt

This project monitors system resource usage (CPU, RAM, GPU) and fetches the latest CO₂ intensity data from the Electricity Map API. It is built using Python and uses Basic Authentication with credentials stored in a `.env` file.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Running Locally (Without a Virtual Environment)](#running-locally-without-a-virtual-environment)
  - [Using a Virtual Environment](#using-a-virtual-environment)
- [Usage](#usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [License](#license)

## Features

- **System Monitoring:** Retrieves CPU, RAM, and GPU usage data.
- **CO₂ Intensity API Call:** Uses the Electricity Map API to fetch current carbon intensity for a specified zone.
- **Secure Credentials:** Stores API credentials in an environment file to avoid hardcoding sensitive data.

## Requirements

- **Python 3.11 or later:** Ensure you have a compatible version of Python installed.
- **pip:** Python package installer.

## Installation

### Running Locally (Without a Virtual Environment)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/TEK-Eget-Projekt.git
   cd TEK-Eget-Projekt
   ```

2. **Install required packages globally:**

   If you have a `requirements.txt` file, run:

   ```bash
   pip install -r requirements.txt
   ```

   If not, install the dependencies manually:

   ```bash
   pip install psutil GPUtil requests python-dotenv
   ```

### Using a Virtual Environment

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/TEK-Eget-Projekt.git
   cd TEK-Eget-Projekt
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - On Windows:
     ```bash
     venvScriptsactivate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install required packages:**

   If you have a `requirements.txt` file, run:

   ```bash
   pip install -r requirements.txt
   ```

   If not, install the dependencies manually:

   ```bash
   pip install psutil GPUtil requests python-dotenv
   ```

## Usage

1. **Configure your environment:**

   Create a `.env` file in the root of the project with the following content:

   ```env
   ELECTRICITY_MAPS_EMAIL=YOUR_ELECTRICITY_MAPS_EMAIL
   ELECTRICITY_MAPS_API_KEY=YOUR_ELECTRICITY_MAPS_API_KEY
   ```

   This file contains your credentials for the Electricity Map API. **Make sure this file is listed in your `.gitignore` to prevent it from being committed.**

2. **Run the project:**

   ```bash
   python system_monitor.py
   ```

   The script will display:
   - CPU usage
   - RAM usage
   - GPU usage
   - CO₂ intensity for the configured zone (default is set to Sweden, zone "SE")

## Configuration

- **Zone Configuration:**  
  The `get_co2_intensity()` function accepts a `zone` parameter. To change the zone (for example, to use a different country code), update the function call in the main block or modify the default value in the function definition.

- **Basic Authentication:**  
  The project uses HTTP Basic Authentication. The credentials (email and API key) are loaded from the `.env` file using `python-dotenv`.

## Troubleshooting

- **API Errors:**  
  If you encounter a `401 Unauthorized` error, double-check your API credentials in the `.env` file and ensure your plan supports external API calls.

- **Dependency Issues:**  
  Ensure all dependencies are installed. You can reinstall them using:
  ```bash
  pip install -r requirements.txt
  ```

- **DNS Resolution Issues:**  
  If you experience errors related to DNS or name resolution (e.g., `getaddrinfo failed`), check your internet connection and DNS settings. You may need to switch to a public DNS server such as Google's (8.8.8.8).

## Project Structure

```
TEK-Eget-Projekt/
├── system_monitor.py    # Main script for system monitoring and API calls
├── .env                 # Environment file for storing sensitive credentials (not committed)
├── .gitignore           # Git ignore file
├── README.md            # This file
└── requirements.txt     # (Optional) List of dependencies
```

## License

This project is licensed under the NULL License. See the [LICENSE](LICENSE) file for details.
