import os
import sqlite3
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('energy_data.db')
    conn.row_factory = sqlite3.Row  # Gör att vi kan hämta rader som dict-liknande objekt
    return conn

@app.route('/')
def index():
    # Hämta den senaste posten från databasen
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM system_data ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    return render_template('index.html', data=data)

@app.route('/api/data', methods=['POST'])
def save_system_data():
    data = request.get_json()
    cpu_usage = data.get('cpu_usage')
    ram_usage = data.get('ram_usage')
    gpu_usage = data.get('gpu_usage')
    co2_intensity = data.get('co2_intensity')

    if cpu_usage is None or ram_usage is None or co2_intensity is None:
        return jsonify({"error": "Måste skicka cpu_usage, ram_usage och co2_intensity"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO system_data (cpu_usage, ram_usage, gpu_usage, co2_intensity)
        VALUES (?, ?, ?, ?)
        """,
        (cpu_usage, ram_usage, gpu_usage, co2_intensity)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Data sparad"}), 201

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
