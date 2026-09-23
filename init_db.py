import sqlite3

conn = sqlite3.connect('monitor.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS monitor_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    cpu TEXT,
    memory_total TEXT,
    memory_available TEXT,
    disk_usage TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    alert_type TEXT,
    message TEXT
)
''')

conn.commit()
conn.close()
print("数据库表创建成功")
