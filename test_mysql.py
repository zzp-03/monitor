import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Zzp911666@',
    database='monitor'
)

cursor = conn.cursor()
cursor.execute('SELECT VERSION()')
result = cursor.fetchone()
print("MySQL 版本:", result[0])

conn.close()
print("连接成功")
