import requests
import time

url = "http://localhost:8001/report"

def collect():
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 采集成功")
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 采集失败: {resp.status_code}")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 采集异常: {e}")

if __name__ == "__main__":
    collect()
