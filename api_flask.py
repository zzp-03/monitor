from flask import Flask, request, jsonify
import os
import time
from datetime import datetime
import requests
import sqlite3

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 读取 /proc/loadavg，返回 1/5/15 分钟平均负载
def get_cpu_load():
    with open('/proc/loadavg', 'r') as f:
        data = f.read().split()
        return data[0] + ' ' + data[1] + ' ' + data[2]

# 读取 /proc/meminfo，返回总内存和可用内存
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

# 执行 df -h /，返回根分区使用率
def get_disk_usage():
    with os.popen('df -h /') as result:
        lines = result.readlines()
        parts = lines[1].split()
        return parts[4]

# 调用 wttr.in，返回指定城市的温度、天气、湿度
def get_weather(city):
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url)
    data = response.json()
    current = data["current_condition"][0]
    temp = current["temp_C"]
    weather = current["weatherDesc"][0]["value"]
    humidity = current["humidity"]
    return temp, weather, humidity

# 把一次采集的数据写入 SQLite
def save_to_db(timestamp, cpu, total, available, disk):
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO monitor_history (timestamp, cpu, memory_total, memory_available, disk_usage)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, cpu, total, available, disk))
    conn.commit()
    conn.close()

# 根路由
@app.route('/')
def root():
    return '访问 /report 查看简报'

# /report：采集数据，写入数据库，返回 JSON
@app.route('/report')
def report():
    city = "平顶山"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cpu = get_cpu_load()
    total, available = get_memory_info()
    disk = get_disk_usage()
    temp, weather, humidity = get_weather(city)
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

# /analyze：调用 Agnes AI 分析系统状态
@app.route('/analyze')
def analyze():
    cpu = get_cpu_load()
    total, available = get_memory_info()
    disk = get_disk_usage()
    prompt = f"当前服务器状态：CPU负载 {cpu}，内存总量 {total}KB，可用内存 {available}KB，磁盘使用率 {disk}。请用一句话分析系统是否正常，如果不正常可能是什么原因。"
    url = "https://apihub.agnes-ai.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-Aa2cHiLTy8XwqDrhYelIE0gGUIjPiPVk3QKhVGeSUpBtgHZ8",
        "Content-Type": "application/json"
    }
    body = {
        "model": "agnes-2.5-flash",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        result = resp.json()
        ai_reply = result["choices"][0]["message"]["content"]
    except Exception as e:
        ai_reply = f"AI 分析失败: {e}"
    return jsonify({
        "cpu": cpu,
        "memory_total": total,
        "memory_available": available,
        "disk_usage": disk,
        "ai_analysis": ai_reply
    })

# /history：查询最近 10 条历史记录
@app.route('/history')
def history():
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, cpu, memory_total, memory_available, disk_usage FROM monitor_history ORDER BY id DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()
    data = []
    for row in rows:
        data.append({
            "time": row[0],
            "cpu": row[1],
            "memory_total": row[2],
            "memory_available": row[3],
            "disk_usage": row[4]
        })
    return jsonify(data)

# /weather?city=城市名：查询指定城市天气
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

# /now：返回当前时间
@app.route('/now')
def get_current_time():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {"time": now}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)
