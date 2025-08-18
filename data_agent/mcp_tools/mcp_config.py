import os
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

class ServerType(Enum):
    """MCP服务器类型"""
    SEC_FETCH = "sec-fetch"
    INVESTMENT_ANALYSIS = "investment-analysis"
    STOCK_QUERY = "stock-query"
    DEMAND_NETWORK = "demand-network"  # 需求网络分析
    CUSTOM = "custom"

@dataclass
class MCPToolMapping:
    """MCP工具映射配置"""
    tool_name: str
    server_type: ServerType
    description: str = ""

@dataclass
class MCPServerConfig:
    """MCP服务器配置"""
    name: str
    server_type: ServerType
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    server_instructions: str = ""
    
    def __post_init__(self):
        # 如果没有提供headers，从环境变量获取API密钥
        if not self.headers:
            api_key_map = {
                ServerType.SEC_FETCH: "MCP_API_KEY",
                ServerType.INVESTMENT_ANALYSIS: "MCP_INVESTMENT_API_KEY",
                ServerType.STOCK_QUERY: "ALPHA_VANTAGE_KEY",
            }
            
            env_key = api_key_map.get(self.server_type)
            if env_key:
                api_key = os.getenv(env_key, f"your-{self.server_type.value}-api-key-here")
                self.headers = {"X-API-Key": api_key}

class MCPConfigManager:
    """MCP配置管理器"""
    
    # 默认端口映射
    DEFAULT_PORTS = {
        ServerType.SEC_FETCH: 8000,
        ServerType.INVESTMENT_ANALYSIS: 8001,
        ServerType.STOCK_QUERY: 8002,
        ServerType.DEMAND_NETWORK: 8003,  # 需求网络分析服务
    }
    
    # 工具到服务器类型的映射
    TOOL_TO_SERVER_TYPE = {
        # SEC财报数据工具
        "sec_financial_data_query": ServerType.SEC_FETCH,
        "sec_13f_institutional_data": ServerType.SEC_FETCH,
        "system_resource_monitor": ServerType.SEC_FETCH,
        
        # 投资分析工具
        "buffett_style_analysis": ServerType.INVESTMENT_ANALYSIS,
        "intrinsic_value_calculation": ServerType.INVESTMENT_ANALYSIS,
        "investment_risk_assessment": ServerType.INVESTMENT_ANALYSIS,
        
        # 股票查询工具
        "stock_price_query": ServerType.STOCK_QUERY,
        "technical_analysis": ServerType.STOCK_QUERY,
        "fundamental_analysis": ServerType.STOCK_QUERY,
        "real_time_market_data": ServerType.STOCK_QUERY,
        
        # 需求网络分析工具
        "demand_network_analysis": ServerType.DEMAND_NETWORK,
        "market_demand_forecasting": ServerType.DEMAND_NETWORK,
        "consumer_behavior_analysis": ServerType.DEMAND_NETWORK,
        "trend_prediction": ServerType.DEMAND_NETWORK,
    }
    
    # 服务器类型到说明的映射
    SERVER_INSTRUCTIONS = {
        ServerType.SEC_FETCH: "SEC财报数据分析服务，支持完整的13F和财务数据查询",
        ServerType.INVESTMENT_ANALYSIS: "SEC投资分析服务，提供巴菲特风格的投资分析功能",
        ServerType.STOCK_QUERY: "Alpha Vantage股票查询服务，提供实时股票数据和技术分析",
        ServerType.DEMAND_NETWORK: "需求网络分析服务，提供市场需求分析和趋势预测功能",
    }
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.tool_mappings: Dict[str, MCPToolMapping] = {}
        self._initialize_default_mappings()
    
    def _initialize_default_mappings(self):
        """初始化默认工具映射"""
        for tool_name, server_type in self.TOOL_TO_SERVER_TYPE.items():
            self.tool_mappings[tool_name] = MCPToolMapping(
                tool_name=tool_name,
                server_type=server_type,
                description=f"{tool_name}工具"
            )
    
    def add_server(self, server_config: MCPServerConfig):
        """添加MCP服务器"""
        self.servers[server_config.name] = server_config
    
    def create_default_servers(self, base_url: str = "http://localhost") -> Dict[str, MCPServerConfig]:
        """创建默认MCP服务器配置"""
        servers = {}
        
        # SEC财报数据服务器
        sec_fetch_server = MCPServerConfig(
            name="sec-fetch-production",
            server_type=ServerType.SEC_FETCH,
            url=f"{base_url}:{self.DEFAULT_PORTS[ServerType.SEC_FETCH]}/mcp",
            server_instructions=self.SERVER_INSTRUCTIONS[ServerType.SEC_FETCH]
        )
        servers[sec_fetch_server.name] = sec_fetch_server
        
        # 投资分析服务器
        investment_server = MCPServerConfig(
            name="sec-investment-analysis",
            server_type=ServerType.INVESTMENT_ANALYSIS,
            url=f"{base_url}:{self.DEFAULT_PORTS[ServerType.INVESTMENT_ANALYSIS]}/mcp",
            server_instructions=self.SERVER_INSTRUCTIONS[ServerType.INVESTMENT_ANALYSIS]
        )
        servers[investment_server.name] = investment_server
        
        # 股票查询服务器
        stock_server = MCPServerConfig(
            name="sec-stock-query",
            server_type=ServerType.STOCK_QUERY,
            url=f"{base_url}:{self.DEFAULT_PORTS[ServerType.STOCK_QUERY]}/mcp",
            server_instructions=self.SERVER_INSTRUCTIONS[ServerType.STOCK_QUERY]
        )
        servers[stock_server.name] = stock_server
        
        # 需求网络分析服务器
        demand_network_server = MCPServerConfig(
            name="demand-network-analysis",
            server_type=ServerType.DEMAND_NETWORK,
            url=f"{base_url}:{self.DEFAULT_PORTS[ServerType.DEMAND_NETWORK]}/mcp",
            server_instructions=self.SERVER_INSTRUCTIONS[ServerType.DEMAND_NETWORK]
        )
        servers[demand_network_server.name] = demand_network_server
        
        return servers
    
    def get_server_for_tool(self, tool_name: str) -> str:
        """根据工具名称获取对应的服务器名称"""
        # 首先检查是否有明确的工具映射
        if tool_name in self.tool_mappings:
            server_type = self.tool_mappings[tool_name].server_type
            # 查找匹配该服务器类型的服务器
            for server_name, server_config in self.servers.items():
                if server_config.server_type == server_type:
                    return server_name
        
        # 如果没有找到明确映射，使用默认映射
        if tool_name in self.TOOL_TO_SERVER_TYPE:
            server_type = self.TOOL_TO_SERVER_TYPE[tool_name]
            # 查找匹配该服务器类型的服务器
            for server_name, server_config in self.servers.items():
                if server_config.server_type == server_type:
                    return server_name
        
        # 如果还是没找到，返回第一个可用的服务器
        if self.servers:
            return list(self.servers.keys())[0]
        
        return ""
    
    def get_mcp_client_config(self) -> Dict[str, Any]:
        """获取MCP客户端配置"""
        mcp_servers = {}
        for server_name, server_config in self.servers.items():
            mcp_servers[server_name] = {
                "type": "sse",
                "url": server_config.url,
                "headers": server_config.headers,
                "serverInstructions": server_config.server_instructions
            }
        
        return {
            "mcpServers": mcp_servers
        }
    
    def update_server_url(self, server_name: str, new_url: str):
        """更新服务器URL"""
        if server_name in self.servers:
            self.servers[server_name].url = new_url
    
    def add_custom_tool_mapping(self, tool_name: str, server_type: ServerType, description: str = ""):
        """添加自定义工具映射"""
        self.tool_mappings[tool_name] = MCPToolMapping(
            tool_name=tool_name,
            server_type=server_type,
            description=description
        )
    
    def get_available_tools(self) -> List[str]:
        """获取所有可用工具列表"""
        return list(self.tool_mappings.keys())