"""
MCP配置使用示例
展示如何使用新的MCP配置管理机制
"""

from data_agent.agent import DataAnalysisAgent, AgentConfig
from data_agent.mcp_tools.mcp_config import MCPConfigManager, MCPServerConfig, ServerType

# 示例1: 使用默认配置（端口800x系列）
def example_default_config():
    """使用默认MCP配置"""
    print("=== 使用默认MCP配置 ===")
    config = AgentConfig(debug_mode=True)
    agent = DataAnalysisAgent(config)
    return agent

# 示例2: 自定义MCP服务器配置
def example_custom_config():
    """自定义MCP服务器配置"""
    print("=== 自定义MCP服务器配置 ===")
    
    # 创建配置管理器
    config_manager = MCPConfigManager()
    
    # 创建自定义服务器配置
    servers = {
        "sec-fetch-production": MCPServerConfig(
            name="sec-fetch-production",
            server_type=ServerType.SEC_FETCH,
            url="http://localhost:8000/mcp",
            server_instructions="SEC财报数据分析服务"
        ),
        "sec-investment-analysis": MCPServerConfig(
            name="sec-investment-analysis",
            server_type=ServerType.INVESTMENT_ANALYSIS,
            url="http://localhost:8001/mcp",
            server_instructions="投资分析服务"
        ),
        "sec-stock-query": MCPServerConfig(
            name="sec-stock-query",
            server_type=ServerType.STOCK_QUERY,
            url="http://localhost:8002/mcp",
            server_instructions="股票查询服务"
        )
    }
    
    # 更新配置管理器
    config_manager.servers = servers
    
    # 获取MCP客户端配置
    mcp_config = config_manager.get_mcp_client_config()
    
    # 创建Agent配置
    config = AgentConfig(
        debug_mode=True,
        mcp_config=mcp_config
    )
    
    # 创建Agent
    agent = DataAnalysisAgent(config)
    return agent

# 示例3: 添加自定义工具映射
def example_custom_tool_mapping():
    """添加自定义工具映射"""
    print("=== 添加自定义工具映射 ===")
    
    # 创建配置管理器
    config_manager = MCPConfigManager()
    
    # 添加自定义工具映射
    config_manager.add_custom_tool_mapping(
        "my_custom_analysis",
        ServerType.INVESTMENT_ANALYSIS,
        "我的自定义分析工具"
    )
    
    # 创建服务器配置
    servers = config_manager.create_default_servers()
    # 更新端口
    for server in servers.values():
        if server.server_type == ServerType.SEC_FETCH:
            server.url = "http://localhost:8000/mcp"
        elif server.server_type == ServerType.INVESTMENT_ANALYSIS:
            server.url = "http://localhost:8001/mcp"
        elif server.server_type == ServerType.STOCK_QUERY:
            server.url = "http://localhost:8002/mcp"
    
    config_manager.servers = servers
    
    # 获取配置
    mcp_config = config_manager.get_mcp_client_config()
    
    # 创建Agent配置
    config = AgentConfig(
        debug_mode=True,
        mcp_config=mcp_config
    )
    
    # 创建Agent
    agent = DataAnalysisAgent(config)
    
    # 查看可用工具
    print("可用工具:", config_manager.get_available_tools())
    
    return agent

if __name__ == "__main__":
    # 运行示例
    agent1 = example_default_config()
    print("默认配置Agent创建成功\n")
    
    agent2 = example_custom_config()
    print("自定义配置Agent创建成功\n")
    
    agent3 = example_custom_tool_mapping()
    print("自定义工具映射Agent创建成功\n")