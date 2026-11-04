import paramiko
import re
from datetime import datetime

# --- 1. 定义一个服务器列表（模拟多台机器）---
servers = [
    {"ip": "192.168.100.4", "user": "root", "pwd": "123456"},  # 这是你真实的虚拟机
    {"ip": "192.168.100.99", "user": "root", "pwd": "123456"}  # 这是一个不存在的假IP，用来测试报错
]


def check_server(host, user, pwd):
    print(f"--- 开始巡检: {host} ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    report_data = ""

    try:
        ssh.connect(hostname=host, port=22, username=user, password=pwd, timeout=3)

        # 1. 抓取磁盘
        stdin, stdout, stderr = ssh.exec_command('df -h /')
        disk_info = stdout.read().decode('utf-8')

        # 2. 抓取内存 (加入数据清洗)
        stdin, stdout, stderr = ssh.exec_command('free -m')
        mem_raw = stdout.read().decode('utf-8')
        # 提取 Mem: 那一行，并拆分
        mem_line = ""  # 准备一个空碗
        for line in mem_raw.split('\n'): # 把文本按换行切开，挨个看
            if line.startswith('Mem:'):  # 找到以 Mem: 开头的那行
                mem_line = line          # 放进碗里
                break                    # 找到了立刻停止
        mem_data = mem_line.split()
        total_mem = int(mem_data[1])
        used_mem = int(mem_data[2])
        mem_percent = round((used_mem / total_mem) * 100, 2)

        # 3. 抓取 CPU 负载
        stdin, stdout, stderr = ssh.exec_command('uptime')
        cpu_info = stdout.read().decode('utf-8')

        # --- 拼装单台机器的报告 ---
        report_data += f"========== 巡检报告: {host} ==========\n"
        report_data += f"巡检时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report_data += f"--- [1] CPU 负载 (uptime) ---\n{cpu_info}\n"
        # 注意这里：用我们算好的百分比替换掉原本的 mem_info
        report_data += f"--- [2] 内存情况 ---\n总内存: {total_mem}MB | 已用: {used_mem}MB | 使用率: {mem_percent}%\n"
        report_data += f"--- [3] 磁盘使用率 (df -h) ---\n{disk_info}\n\n"
        print(f"✅ {host} 巡检成功！")

    except Exception as e:
        # 容错处理：一台连不上，绝不崩溃，记下错误继续下一台
        print(f"❌ {host} 连接失败: {e}")
        report_data = f"========== 巡检报告: {host} ==========\n❌ 连接失败: {e}\n\n"
    finally:
        ssh.close()
        return report_data


# --- 2. 核心逻辑：循环遍历所有机器 ---
print("🚀 批量巡检任务启动...")
all_reports = ""  # 用来装所有机器的报告

for server in servers:
    # 依次调用函数，把单台的结果拼到总报告里
    result = check_server(server["ip"], server["user"], server["pwd"])
    all_reports += result

# --- 3. 统一保存到一个文件 ---
filename = f"批量巡检报告_{datetime.now().strftime('%Y%m%d')}.log"
with open(filename, 'w', encoding='utf-8') as f:
    f.write(all_reports)

print(f"\n🎉 全部巡检完成！汇总报告已保存至: {filename}")
