# 数据分析Agent

一个轻量级的数据分析Agent，具有以下特性：

1. 调用MCP工具进行数据分析
2. 自动处理时间参数转换（如将"最近"转换为具体日期范围）
3. 能够调用多个MCP工具完成复杂分析
4. 具备调试能力，可观察LLM和MCP的输入输出
5. 良好的prompt管理
6. 使用langfuse进行调试跟踪
7. 错误自动恢复机制
8. 支持相对时间表达式解析
9. 支持多种LLM（Qwen、DeepSeek等）
10. 支持多种专业MCP服务（SEC数据、投资分析、股票查询等）

## 特性

### MCP工具调用
- 支持调用多个MCP工具
- 自动错误恢复机制
- 结果缓存优化
- 支持多个MCP端点负载均衡

### 智能时间处理
- 自动将"最近"、"过去X天"等相对时间转换为具体日期范围
- 支持天、周、月等时间单位
- 支持中文表达式如"最近几天"、"过去几周"等
- 自动处理日期计算和格式化

### 错误恢复机制
- MCP工具调用失败时自动重试
- 支持降级到备用工具或返回缓存数据
- 记录详细的错误日志便于调试
- 即使部分工具调用失败也能继续执行其他工具

### 调试能力
- 跟踪LLM的输入输出
- 跟踪MCP工具的调用参数和结果
- 集成Langfuse进行高级调试

### Prompt管理
- 集中式Prompt管理
- 可动态加载和更新Prompt模板

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```python
from data_agent.agent import DataAnalysisAgent, AgentConfig

# 配置Agent
config = AgentConfig(
    mcp_endpoints=["http://localhost:8000/api"],
    debug_mode=True,
    langfuse_enabled=True,
    default_llm="qwen"  # 可选: "qwen", "deepseek", 或其他支持的LLM
)

# 创建Agent实例
agent = DataAnalysisAgent(config)

# 处理用户查询
result = await agent.process_query("帮我看看最近30天的销售数据")
print(result)
```

## LLM配置

在 `.env` 文件中配置API密钥：

```env
# Qwen API Key
DASHSCOPE_API_KEY=your_qwen_api_key_here

# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## MCP服务配置

Agent支持以下MCP服务：

1. **SEC财报数据服务** (端口 8000)
   - 功能: SEC财报数据、13F机构数据、系统资源监控
   - 端点: http://localhost:8000/mcp

2. **投资分析服务** (端口 8001)
   - 功能: 巴菲特风格投资分析、内在价值计算
   - 端点: http://localhost:8001/mcp

3. **股票查询服务** (端口 8002)
   - 功能: Alpha Vantage股票数据、实时行情
   - 端点: http://localhost:8002/mcp

在 `.env` 文件中配置MCP API密钥：

```env
# MCP API Keys
MCP_API_KEY=your-sec-fetch-api-key-here
MCP_INVESTMENT_API_KEY=your-investment-analysis-api-key-here
ALPHA_VANTAGE_KEY=your-alpha-vantage-api-key-here
```

## 使用示例

### 基本使用
```bash
# 运行测试
python -m data_agent.test_agent

# 运行演示
python -m data_agent.demo

# 运行投资分析测试
python -m data_agent.test_investment
```

### 相对时间表达式示例
Agent支持以下相对时间表达式：
- "最近7天" / "过去7天"
- "最近几周" / "过去2周"
- "最近几个月" / "过去3个月"
- "最近几天"

### 复杂查询示例
```python
# 复杂的数据分析请求
queries = [
    "帮我分析最近30天的销售数据，按周分组",
    "查看最近一周的用户活跃度，并与上个月同期对比",
    "分析产品A和产品B在过去三个月的performance，并给出建议"
]
```

### Web客户端使用
```bash
# 启动Web服务
cd data_agent/webclient
./start.sh

# 或者直接运行
python server.py
```

访问 `http://localhost:8080` 使用Web聊天界面与数据分析Agent交互。

#### Web客户端特性
- 实时聊天界面，支持输入框和按钮发送消息
- 支持Enter键快速发送消息
- JSON格式响应的自动解析和格式化显示
- 正在输入指示器动画效果
- 响应式设计，适配不同屏幕尺寸
- 深色模式支持
- WebSocket实时通信支持

#### WebSocket API
Web客户端还提供了WebSocket接口用于实时通信：
- WebSocket端点: `ws://localhost:8080/api/ws`
- 发送消息格式: `{"message": "您的查询内容"}`
- 接收响应格式: `{"response": "响应内容", "status": "success"}`

#### 测试Web客户端
```bash
# 运行Web客户端测试
python -m data_agent.test_webclient
```

## 架构设计

```
data_agent/
├── agent.py              # 主Agent类
├── main.py               # 使用示例
├── demo.py               # 演示程序
├── full_demo.py          # 完整功能演示
├── test_agent.py         # 基本测试
├── test_llm.py           # LLM集成测试
├── test_mcp.py           # MCP集成测试
├── test_investment.py    # 投资分析测试
├── requirements.txt      # 依赖列表
├── .env                  # 环境变量配置
├── .env.example          # 环境变量示例
├── README.md             # 项目文档
├── Dockerfile            # Docker配置
├── install.sh            # 安装脚本
├── mcp_tools/           # MCP工具相关
│   ├── mcp_client.py    # MCP客户端
│   └── mcp_simulator.py # MCP模拟器
├── utils/               # 工具模块
│   └── debug.py         # 调试管理器
├── prompts/             # Prompt管理
│   └── prompt_manager.py # Prompt管理器
├── llm/                 # LLM集成
│   ├── llm_manager.py   # LLM管理器
│   ├── qwen_llm.py      # Qwen集成
│   └── deepseek_llm.py  # DeepSeek集成
└── webclient/           # Web客户端
    ├── index.html       # 前端界面
    ├── server.py        # Web服务后端
    └── start.sh         # 启动脚本
```

## 扩展

### 添加新的MCP工具
1. 在`mcp_client.py`中的`get_available_tools`方法添加工具名称
2. 实现具体的工具调用逻辑

### 自定义Prompt
1. 在`prompt_manager.py`中添加新的prompt模板
2. 在Agent中使用新的prompt名称

### 配置调试
1. 设置`debug_mode=True`启用调试日志
2. 设置`langfuse_enabled=True`并配置Langfuse API密钥