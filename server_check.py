import paramiko
from datetime import datetime
import concurrent.futures
import os   # 新增这一行

# 你的服务器列表
servers = [
    {"ip": "192.168.100.4", "user": "root", "pwd": os.environ.get("SRV1_PWD", "")}, 
    {"ip": "192.168.100.99", "user": "root", "pwd": os.environ.get("SRV2_PWD", "")}      
]

def check_server(host, user, pwd):
    print(f"--- 开始巡检: {host} ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    report_data = ""

    try:
        # timeout=3 极其重要，防止卡死
        ssh.connect(hostname=host, port=22, username=user, password=pwd, timeout=3)
        
        stdin, stdout, stderr = ssh.exec_command('df -h /')
        disk_info = stdout.read().decode('utf-8')
        
        stdin, stdout, stderr = ssh.exec_command('free -m')
        mem_raw = stdout.read().decode('utf-8')
        
        mem_line = ""  
        for line in mem_raw.split('\n'): 
            if line.startswith('Mem:'):  
                mem_line = line          
                break                    
                
        mem_data = mem_line.split()
        total_mem = int(mem_data[1])
        used_mem = int(mem_data[2])
        mem_percent = round((used_mem / total_mem) * 100, 2)
        
        stdin, stdout, stderr = ssh.exec_command('uptime')
        cpu_info = stdout.read().decode('utf-8')

        report_data += f"========== 巡检报告: {host} ==========\n"
        report_data += f"巡检时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}E,E,E,E,E,E,\n\n"
        report_data += f"--- [1] CPU 负载 ---\n{cpu_info}\n"
        report_data += f"--- [2] 内存情况 ---\n总内存: {total_mem}MB | 已用: {used_mem}MB | 使用率: {mem_percent}%\n"
        report_data += f"--- [3] 磁盘使用率 ---\n{disk_info}\n\n"
        print("✅ " + host + " 巡检成功！")

    except Exception as e:
        print(f"❌ {host} 连接失败: {e}")
        report_data = f"========== 巡检报告: {host} ==========\n❌ 连接失败: {e}\n\n"
    finally:
        ssh.close()
        return report_data

# ====== 下面是多线程执行区 ======
print("🚀 并发巡检任务启动（多线程模式）...")
all_reports = ""

# 开启线程池，最大并发数设为 5（也就是一次同时查 5 台）
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for server in servers:
        # 提交任务，不等待
        future = executor.submit(check_server, server["ip"], server["user"], server["pwd"])
        futures.append(future)

    # 谁先干完，谁先回传结果
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        all_reports += result

# 写入日志文件
filename = f"批量巡检报告_{datetime.now().strftime('%Y%m%d')}.log"
with open(filename, 'w', encoding='utf-8') as f:
    f.write(all_reports)

print(f"\n🎉 全部巡检完成！汇总报告已保存至: {filename}")
