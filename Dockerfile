# 用 Python 3.9 做基础镜像（比 CentOS 7 自带的 3.6 新）
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 装依赖，用清华源加速
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制项目代码
COPY api_flask.py .
COPY templates ./templates

# 暴露 8001 端口
EXPOSE 8001

# 启动命令
CMD ["python", "api_flask.py"]
