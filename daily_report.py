import os
import time
import requests
from datetime import datetime

# ===== 从 check_system.py 复制过来的函数 =====
def get_cpu_load():
    with open('/proc/loadavg', 'r') as f:
        data = f.read().split()
        return data[0] + ' ' + data[1] + ' ' + data[2]

def get_memory_info():
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()
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

# ===== 从 weather_report.py 复制过来的函数 =====
def get_weather(city):
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url)
    data = response.json()
    current = data["current_condition"][0]
    temp = current["temp_C"]
    weather = current["weatherDesc"][0]["value"]
    humidity = current["humidity"]
    return temp, weather, humidity

# ===== 主程序 =====
if __name__ == "__main__":
    city = input("请输入城市名：")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cpu = get_cpu_load()
    total, available = get_memory_info()
    disk = get_disk_usage()
    temp, weather, humidity = get_weather(city)

    print("=" * 30)
    print("每日简报")
    print(f"时间：{timestamp}")
    print("--- 系统状态 ---")
    print(f"CPU负载：{cpu}")
    print(f"内存总量：{total}KB")
    print(f"可用内存：{available}KB")
    print(f"磁盘使用率：{disk}")
    print("--- 天气 ---")
    print(f"城市：{city}")
    print(f"温度：{temp}°C")
    print(f"天气：{weather}")
    print(f"湿度：{humidity}%")
    print("=" * 30)

    with open("daily.log", "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | CPU:{cpu} | 内存:{total}/{available}KB | 磁盘:{disk} | {city} {temp}°C {weather}\n")
