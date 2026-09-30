import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Zzp911666@',
    database='monitor'
)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS monitor_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp VARCHAR(50),
    cpu VARCHAR(50),
    memory_total VARCHAR(50),
    memory_available VARCHAR(50),
    disk_usage VARCHAR(50)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS alert_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp VARCHAR(50),
    alert_type VARCHAR(20),
    message VARCHAR(255)
)
''')

conn.commit()
conn.close()
print("数据库表创建成功")
