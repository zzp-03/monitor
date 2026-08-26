import requests
from datetime import datetime

city = input("请输入城市名：")

url = f"https://wttr.in/{city}?format=j1"

response = requests.get(url)
data = response.json()

current = data["current_condition"][0]
temp = current["temp_C"]
weather = current["weatherDesc"][0]["value"]
humidity = current["humidity"]

print("=" * 30)
print(f"{city} 天气简报")
print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"温度：{temp}°C")
print(f"天气：{weather}")
print(f"湿度：{humidity}%")
print("=" * 30)

with open("weather.log", "a", encoding="utf-8") as f:
    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | {city} | {temp}°C | {weather} | {humidity}%\n")
