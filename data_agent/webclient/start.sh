#!/bin/bash
# 启动Web客户端和数据分析Agent服务

echo "正在启动数据分析Agent Web服务..."

# 激活虚拟环境
source ../venv/bin/activate

# 启动Web服务
python server.py