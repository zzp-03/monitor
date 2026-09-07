from flask import Flask, request, jsonify
import os
import time
from datetime import datetime
import requests
import sqlite3

app = Flask(__name__)

def get_cpu_load():
    with open('/proc/loadavg', 'r') as f:
        data = f.read().split()
        return data[0] + ' ' + data[1] + ' ' + data[2]

def get_memory_info():
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()
        total = "0"
        available = "0"
        for line in lines:
            if 'MemTotal' in line:
                total = line.split()[1]
            if 'MemAvailable' in line:
                available = line.split()[1]
        return total, available

def get_disk_usage():
    with os.popen('df -h /') as result:
        lines = result.readlines()
        parts = lines[1].split()
        return parts[4]

def get_weather(city):
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url)
    data = response.json()
    current = data["current_condition"][0]
    temp = current["temp_C"]
    weather = current["weatherDesc"][0]["value"]
    humidity = current["humidity"]
    return temp, weather, humidity

def save_to_db(timestamp, cpu, total, available, disk):
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO monitor_history (timestamp, cpu, memory_total, memory_available, disk_usage)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, cpu, total, available, disk))
    conn.commit()
    conn.close()

@app.route('/')
def root():
    return '访问 /report 查看简报'

@app.route('/report')
def report():
    city = "平顶山"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cpu = get_cpu_load()
    total, available = get_memory_info()
    disk = get_disk_usage()
    temp, weather, humidity = get_weather(city)

    # 保存到数据库
    save_to_db(timestamp, cpu, total, available, disk)

    return jsonify({
        "time": timestamp,
        "cpu": cpu,
        "memory_total": total,
        "memory_available": available,
        "disk_usage": disk,
        "city": city,
        "temperature": temp,
        "weather": weather,
        "humidity": humidity
    })

@app.route('/weather')
def get_weather_api():
    city = request.args.get('city')
    if not city:
        return {"error": "请提供城市名，例如 /weather?city=北京"}
    temp, weather, humidity = get_weather(city)
    return {
        "city": city,
        "temperature": temp,
        "weather": weather,
        "humidity": humidity
    }

@app.route('/now')
def get_current_time():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {"time": now}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)
