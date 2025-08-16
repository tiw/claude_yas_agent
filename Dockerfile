# 使用官方Python运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到容器中
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8080 9000 9001 9002

# 定义环境变量
ENV PYTHONPATH=/app

# 运行应用
CMD ["python", "data_agent/webclient/server.py"]