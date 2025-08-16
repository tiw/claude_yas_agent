# 数据分析Agent

一个功能完整的轻量级数据分析Agent，能够理解自然语言查询并自动执行复杂的数据分析任务。

## 核心特性

### 智能数据分析
- **自然语言理解**：将用户查询自动解析为结构化分析任务
- **多维度分析**：支持财务数据、投资价值、股票行情等多种分析类型
- **复杂任务执行**：能够调用多个工具完成组合分析任务
- **结构化报告**：自动生成包含执行摘要、详细分析、关键洞察和建议的完整报告

### MCP工具集成
- **多服务架构**：集成SEC财务数据、投资分析、股票查询三个专业MCP服务
- **智能路由**：根据工具类型自动选择合适的MCP服务器
- **负载均衡**：支持多个MCP端点的负载分配
- **健康检查**：初始化时自动检测MCP服务器健康状态

### 多LLM支持
- **Qwen（通义千问）**：默认使用的高性能中文模型
- **DeepSeek**：支持的代码生成优化模型
- **可扩展设计**：易于添加新的大语言模型支持

## 高级功能

### 智能时间处理
- **相对时间解析**：自动将"最近几天"、"过去几周"等表达式转换为具体日期范围
- **时间单位支持**：支持天、周、月等时间单位的智能计算
- **自动格式化**：自动生成标准化的日期范围和格式

### 完善的错误恢复
- **自动重试机制**：MCP工具调用失败时自动重试
- **降级策略**：支持降级到备用工具或返回缓存数据
- **容错设计**：即使部分工具失败也能继续执行其他分析任务

### 全面调试能力
- **多层级跟踪**：全程跟踪LLM输入输出和MCP工具调用
- **会话管理**：支持多会话并行调试，日志隔离
- **实时监控**：Web界面实时显示调试信息
- **Langfuse集成**：支持高级调试跟踪和性能分析

### 灵活配置管理
- **环境变量配置**：通过.env文件安全配置API密钥和端点
- **编程配置**：支持通过AgentConfig对象动态配置
- **自定义MCP服务**：支持配置正式的MCP服务URL和认证信息

## 技术架构

### 现代化技术栈
- **异步架构**：基于aiohttp的全异步设计，支持高并发处理
- **模块化设计**：清晰的架构分层，易于扩展和维护
- **标准化接口**：RESTful API和WebSocket双接口支持

### 完整的Web界面
- **聊天交互界面**：响应式设计，支持桌面和移动端使用
- **调试监控面板**：实时查看分析过程和调试信息
- **会话管理**：可按会话查看历史分析记录

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用
```python
from data_agent.agent import DataAnalysisAgent, AgentConfig

# 配置Agent
config = AgentConfig(
    debug_mode=True,
    langfuse_enabled=False,
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

1. **SEC财报数据服务** (端口 9000)
   - 功能: SEC财报数据、13F机构数据、系统资源监控
   - 端点: http://localhost:9000/mcp

2. **投资分析服务** (端口 9001)
   - 功能: 巴菲特风格投资分析、内在价值计算
   - 端点: http://localhost:9001/mcp

3. **股票查询服务** (端口 9002)
   - 功能: Alpha Vantage股票数据、实时行情
   - 端点: http://localhost:9002/mcp

在 `.env` 文件中配置MCP API密钥：

```env
# MCP API Keys
MCP_API_KEY=your-sec-fetch-api-key-here
MCP_INVESTMENT_API_KEY=your-investment-analysis-api-key-here
ALPHA_VANTAGE_KEY=your-alpha-vantage-api-key-here
```

### 配置正式MCP服务

要使用正式的MCP服务，您可以通过以下方式配置：

#### 方法1：通过环境变量配置API密钥
在 `.env` 文件中设置正式的API密钥：
```env
# 正式MCP API Keys
MCP_API_KEY=your_production_sec_fetch_api_key
MCP_INVESTMENT_API_KEY=your_production_investment_analysis_api_key
ALPHA_VANTAGE_KEY=your_production_alpha_vantage_key
```

#### 方法2：通过AgentConfig配置自定义MCP服务URL
```python
from data_agent.agent import DataAnalysisAgent, AgentConfig

# 配置正式的MCP服务
config = AgentConfig(
    debug_mode=True,
    langfuse_enabled=False,
    default_llm="qwen",
    mcp_config={
        "mcpServers": {
            "sec-fetch-production": {
                "type": "sse",
                "url": "https://api.sec-data.com/mcp",
                "headers": {
                    "X-API-Key": "your_production_sec_fetch_api_key"
                },
                "serverInstructions": "SEC财报数据分析服务，支持完整的13F和财务数据查询"
            },
            "sec-investment-analysis": {
                "type": "sse",
                "url": "https://api.investment-analysis.com/mcp",
                "headers": {
                    "X-API-Key": "your_production_investment_analysis_api_key"
                },
                "serverInstructions": "SEC投资分析服务，提供巴菲特风格的投资分析功能"
            },
            "sec-stock-query": {
                "type": "sse",
                "url": "https://api.alpha-vantage.com/mcp",
                "headers": {
                    "X-API-Key": "your_production_alpha_vantage_key"
                },
                "serverInstructions": "Alpha Vantage股票查询服务，提供实时股票数据和技术分析"
            }
        }
    }
)

# 创建Agent实例
agent = DataAnalysisAgent(config)
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

访问 `http://localhost:8083` 使用Web聊天界面与数据分析Agent交互。

### 调试监控使用
访问 `http://localhost:8083/debug-monitor.html` 查看调试监控界面：
- 实时查看LLM输入输出和MCP调用详情
- 按会话分组查看分析过程
- 统计信息展示和日志过滤
- WebSocket实时推送调试信息

## 架构设计

```
data_agent/
├── agent.py              # 主Agent类
├── main.py               # 使用示例
├── demo.py               # 演示程序
├── full_demo.py          # 完整功能演示
├── production_mcp_example.py # 正式MCP配置示例
├── test_agent.py         # 基本测试
├── test_llm.py           # LLM集成测试
├── test_mcp.py           # MCP集成测试
├── test_investment.py    # 投资分析测试
├── test_session_debug.py # 会话调试测试
├── test_webclient.py     # Web客户端测试
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
    ├── __init__.py      # 包初始化
    ├── index.html       # 前端界面
    ├── debug_monitor.html # 调试监控界面
    ├── server.py        # Web服务后端
    ├── start.sh         # 启动脚本
    ├── test_debug_api.py # 调试API测试
    └── websocket_test.html # WebSocket测试页面
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

## 主要改进和新增功能

### 新增功能
1. **多LLM支持**：除了Qwen，还支持DeepSeek等多种大语言模型
2. **相对时间处理**：智能化解析"最近几天"、"过去几周"等自然时间表达式
3. **专业MCP服务集成**：集成SEC财务数据、投资分析、股票查询等多个专业MCP服务
4. **Web可视化界面**：提供完整的前端界面，支持聊天交互和调试监控
5. **WebSocket实时通信**：支持双向实时通信，提升用户体验
6. **会话管理机制**：支持多用户并行使用，会话隔离
7. **多层级缓存机制**：工具调用结果缓存，提升性能
8. **动态Prompt管理**：集中化Prompt管理，支持动态更新
9. **完善的错误恢复**：多种恢复策略，确保服务稳定性
10. **外部监控集成**：Langfuse集成，支持高级调试跟踪

### 技术改进
1. **异步化架构**：全面采用异步编程，提升并发处理能力
2. **结构化响应**：统一的JSON响应格式，便于解析和展示
3. **模块化设计**：清晰的架构分层，易于扩展和维护
4. **完整的调试能力**：从LLM输入输出到MCP调用全程可追溯
5. **负载均衡支持**：多个MCP服务的智能路由和负载分配
6. **增强的配置管理**：支持环境变量和编程配置双重方式
7. **安全性提升**：API密钥安全存储，头部信息配置

### 架构演进规划
项目已制定详细的架构改进路线图，参考 [ARCHITECTURE_IMPROVEMENT_ROADMAP.md](ARCHITECTURE_IMPROVEMENT_ROADMAP.md)：
- **短期目标**：模块化重构、统一工具抽象、完善错误处理
- **中期目标**：Memory管理、流式响应、并行执行
- **长期目标**：可插拔架构、性能优化、插件生态系统

### Pydantic-AI理念改进
基于Pydantic-AI框架的设计理念，项目制定了详细的改进方案，参考 [PYDANTIC_AI_IMPROVEMENTS.md](PYDANTIC_AI_IMPROVEMENTS.md)：
- **类型安全**：引入Pydantic模型验证，确保数据结构正确性
- **API简化**：借鉴Pydantic-AI的简洁API设计
- **工具装饰器**：实现类似`@agent.tool`的工具定义方式
- **依赖注入**：支持灵活的运行时依赖注入机制