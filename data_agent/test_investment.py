#!/usr/bin/env python3
"""
投资分析测试
专门测试投资相关的查询
"""

import asyncio
import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_agent.agent import DataAnalysisAgent, AgentConfig

# 配置日志
logging.basicConfig(level=logging.INFO)

async def test_investment_queries():
    """测试投资相关查询"""
    print("投资分析测试")
    print("=" * 50)
    
    try:
        # 配置Agent
        config = AgentConfig(
            debug_mode=True,
            langfuse_enabled=False,
            default_llm="qwen"
        )
        
        agent = DataAnalysisAgent(config)
        
        # 投资相关测试查询
        investment_queries = [
            "查询苹果公司(AAPL)最近一季度的财务数据",
            "分析特斯拉(TSLA)的巴菲特风格投资价值",
            "获取微软(MSFT)的实时股价和技术分析",
            "计算亚马逊(AMZN)的内在价值",
            "评估谷歌(GOOG)的投资风险"
        ]
        
        for i, query in enumerate(investment_queries, 1):
            print(f"\n[{i}] 用户查询: {query}")
            print("-" * 40)
            
            try:
                result = await agent.process_query(query)
                print("处理结果:")
                print(result[:300] + "..." if len(result) > 300 else result)
                
                # 显示调试信息
                mcp_calls = [log for log in agent.debug_manager.logs if log['type'] == 'mcp_input']
                print(f"MCP调用次数: {len(mcp_calls)}")
                
            except Exception as e:
                print(f"处理查询时出错: {e}")
            
            # 清空日志以准备下一个查询
            agent.debug_manager.clear_logs()
                
    except Exception as e:
        print(f"投资分析测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_investment_queries())