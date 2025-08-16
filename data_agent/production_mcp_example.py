#!/usr/bin/env python3
"""
正式MCP服务配置示例
演示如何配置数据分析Agent使用正式的MCP服务
"""

import asyncio
import logging
from data_agent.agent import DataAnalysisAgent, AgentConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """主函数"""
    # 配置正式的MCP服务
    config = AgentConfig(
        debug_mode=True,
        langfuse_enabled=False,
        default_llm="qwen",
        mcp_config={
            "mcpServers": {
                "sec-fetch-production": {
                    "type": "sse",
                    "url": "https://api.sec-data.com/mcp",  # 正式SEC数据服务URL
                    "headers": {
                        "X-API-Key": "your_production_sec_fetch_api_key"  # 替换为实际API密钥
                    },
                    "serverInstructions": "SEC财报数据分析服务，支持完整的13F和财务数据查询"
                },
                "sec-investment-analysis": {
                    "type": "sse",
                    "url": "https://api.investment-analysis.com/mcp",  # 正式投资分析服务URL
                    "headers": {
                        "X-API-Key": "your_production_investment_analysis_api_key"  # 替换为实际API密钥
                    },
                    "serverInstructions": "SEC投资分析服务，提供巴菲特风格的投资分析功能"
                },
                "sec-stock-query": {
                    "type": "sse",
                    "url": "https://api.alpha-vantage.com/mcp",  # 正式股票查询服务URL
                    "headers": {
                        "X-API-Key": "your_production_alpha_vantage_key"  # 替换为实际API密钥
                    },
                    "serverInstructions": "Alpha Vantage股票查询服务，提供实时股票数据和技术分析"
                }
            }
        }
    )
    
    # 创建Agent实例
    agent = DataAnalysisAgent(config)
    
    # 示例查询
    queries = [
        "帮我看看苹果公司最近一季度的财务数据",
        "分析一下特斯拉的投资价值",
        "获取微软的实时股价和技术分析"
    ]
    
    # 处理查询
    for query in queries:
        print(f"\n{'='*50}")
        print(f"用户查询: {query}")
        print('='*50)
        
        try:
            result = await agent.process_query(query)
            print(f"Agent回复:\n{result}")
        except Exception as e:
            print(f"处理查询时出错: {e}")
        
        # 显示调试信息
        if agent.debug_manager.logs:
            print(f"\n调试信息 (最近3条):")
            for log in agent.debug_manager.logs[-3:]:
                print(f"  [{log['timestamp']}] {log['type']}: {str(log.get('tool_name', '')) or str(log.get('error', ''))[:50]}...")

if __name__ == "__main__":
    asyncio.run(main())