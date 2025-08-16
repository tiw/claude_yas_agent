#!/bin/bash
# 安装脚本

echo "正在安装数据分析Agent的依赖..."

# 检查是否安装了pip
if ! command -v pip3 &> /dev/null
then
    echo "错误: 未找到pip3。请先安装Python和pip。"
    exit 1
fi

# 安装依赖
pip3 install -r requirements.txt

echo "依赖安装完成!"

echo "正在安装开发依赖 (可选)..."
pip3 install pytest pytest-asyncio black flake8

echo "安装完成! 您可以通过以下方式运行系统:"
echo ""
echo "1. 命令行方式:"
echo "   python3 -m data_agent.test_agent"
echo ""
echo "2. Web客户端方式:"
echo "   cd data_agent/webclient"
echo "   python3 server.py"
echo "   然后在浏览器中访问 http://localhost:8080"
echo ""
echo "3. Docker方式 (如果已安装Docker):"
echo "   docker build -t data-agent ."
echo "   docker run -p 8080:8080 -p 9000-9002:9000-9002 data-agent"