import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import aiohttp
import json
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class MCPClient:
    """MCP客户端，用于调用各种MCP工具"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        self.tools_cache = {}
        self.server_info = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self._initialize_servers()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def _initialize_servers(self):
        """初始化MCP服务器信息"""
        for server_name, server_config in self.config.get("mcpServers", {}).items():
            try:
                url = server_config["url"]
                health_url = url.replace("/mcp", "/health")
                
                async with self.session.get(health_url) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        self.server_info[server_name] = {
                            "url": url,
                            "healthy": True,
                            "health_data": health_data,
                            "headers": server_config.get("headers", {}),
                            "instructions": server_config.get("serverInstructions", "")
                        }
                        logger.info(f"MCP服务器 {server_name} 健康检查通过")
                    else:
                        self.server_info[server_name] = {
                            "url": url,
                            "healthy": False,
                            "headers": server_config.get("headers", {}),
                            "instructions": server_config.get("serverInstructions", "")
                        }
                        logger.warning(f"MCP服务器 {server_name} 健康检查失败")
            except Exception as e:
                logger.error(f"初始化MCP服务器 {server_name} 时出错: {e}")
                self.server_info[server_name] = {
                    "url": server_config["url"],
                    "healthy": False,
                    "headers": server_config.get("headers", {}),
                    "instructions": server_config.get("serverInstructions", "")
                }
    
    def get_available_tools(self) -> List[str]:
        """获取可用的MCP工具列表"""
        # 返回示例工具列表，实际应用中应该从MCP服务动态获取
        return [
            # 通用MCP服务工具
            "sec_financial_data_query",
            "sec_13f_institutional_data",
            "system_resource_monitor",
            
            # 投资分析MCP服务工具
            "buffett_style_analysis",
            "intrinsic_value_calculation",
            "investment_risk_assessment",
            
            # 股票查询MCP服务工具
            "stock_price_query",
            "technical_analysis",
            "fundamental_analysis",
            "real_time_market_data"
        ]
        
    def get_server_instructions(self) -> Dict[str, str]:
        """获取各服务器的使用说明"""
        return {
            server_name: info["instructions"] 
            for server_name, info in self.server_info.items()
        }
        
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用指定的MCP工具"""
        try:
            # 检查是否有缓存的结果
            cache_key = f"{tool_name}_{hash(str(parameters))}"
            if cache_key in self.tools_cache:
                logger.info(f"从缓存返回工具 {tool_name} 的结果")
                return self.tools_cache[cache_key]
            
            # 查找合适的服务器
            server_info = await self._find_server_for_tool(tool_name)
            if not server_info:
                raise ValueError(f"未找到工具 {tool_name} 的可用服务器")
            
            # 构建请求
            url = f"{server_info['url']}/tools/{tool_name}"
            payload = {
                "parameters": parameters,
                "timestamp": datetime.now().isoformat()
            }
            
            # 发送请求
            result = await self._send_request(url, payload, server_info["headers"])
            
            # 缓存结果
            self.tools_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"调用工具 {tool_name} 时出错: {e}")
            # 尝试恢复机制
            return await self._recover_from_error(tool_name, parameters, e)
            
    async def _find_server_for_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """为工具查找合适的服务器"""
        # 根据工具名称匹配服务器
        tool_to_server_mapping = {
            # 通用MCP服务工具
            "sec_financial_data_query": "sec-fetch-production",
            "sec_13f_institutional_data": "sec-fetch-production",
            "system_resource_monitor": "sec-fetch-production",
            
            # 投资分析MCP服务工具
            "buffett_style_analysis": "sec-investment-analysis",
            "intrinsic_value_calculation": "sec-investment-analysis",
            "investment_risk_assessment": "sec-investment-analysis",
            
            # 股票查询MCP服务工具
            "stock_price_query": "sec-stock-query",
            "technical_analysis": "sec-stock-query",
            "fundamental_analysis": "sec-stock-query",
            "real_time_market_data": "sec-stock-query"
        }
        
        server_name = tool_to_server_mapping.get(tool_name)
        if server_name and server_name in self.server_info:
            server_info = self.server_info[server_name]
            if server_info["healthy"]:
                return server_info
        
        # 如果没有找到特定的服务器，返回第一个健康的服务器
        for server_info in self.server_info.values():
            if server_info["healthy"]:
                return server_info
                
        return None
        
    async def _send_request(self, url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """发送HTTP请求到MCP服务"""
        if not self.session:
            raise RuntimeError("MCP客户端未初始化")
            
        try:
            # 添加默认headers
            request_headers = {
                "Content-Type": "application/json",
                **headers
            }
            
            async with self.session.post(url, json=payload, headers=request_headers, timeout=30) as response:
                if response.status == 200:
                    result_data = await response.json()
                    return {
                        "status": "success",
                        "url": url,
                        "parameters": payload["parameters"],
                        "result": result_data,
                        "execution_time": 0  # 实际应用中应该测量执行时间
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"MCP服务返回错误: {response.status} - {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP请求失败: {str(e)}")
        except asyncio.TimeoutError:
            raise Exception("MCP服务请求超时")
        except Exception as e:
            raise Exception(f"发送请求时出错: {str(e)}")
        
    async def _recover_from_error(self, tool_name: str, parameters: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """从错误中恢复"""
        logger.warning(f"尝试从错误中恢复: {error}")
        
        # 可以实现多种恢复策略：
        # 1. 重试机制
        # 2. 降级到备用工具
        # 3. 使用缓存数据
        # 4. 返回默认值或空结果
        
        # 简单恢复：返回错误信息
        return {
            "status": "error",
            "tool": tool_name,
            "parameters": parameters,
            "error": str(error),
            "recovery_action": "returned_error_info"
        }