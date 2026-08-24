import os
import time

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
if __name__ == '__main__':
    cpu = get_cpu_load()
    disk = get_disk_usage()
    total, available = get_memory_info()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    result = f'{timestamp} | CPU负载: {cpu} | 内存总量: {total}KB | 可用内存: {available}KB | 磁盘使用率：{disk}'
    cpu_load = float(cpu.split()[0])
    if cpu_load > 1.0:
        result = result + " | WARNING: CPU load is high"
    disk_usage = int(disk.rstrip('%'))
    if disk_usage > 80:
        result = result + " | WARNING: Disk usage is high"
    print(result)
    with open('status.log', 'a') as f:
        f.write(result + '\n')
