#!/usr/bin/env python3
"""
数据分析Agent主程序
演示如何使用DataAnalysisAgent进行数据分析
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
    # 配置Agent（使用默认MCP配置）
    config = AgentConfig(
        debug_mode=True,
        langfuse_enabled=False,
        default_llm="qwen"  # 可以根据需要改为"deepseek"
    )
    
    # 创建Agent实例
    agent = DataAnalysisAgent(config)
    
    # 示例查询
    queries = [
        "帮我看看最近30天的销售数据",
        "分析一下用户行为，特别是最近一个月的活跃用户数",
        "比较一下我们两个产品线的 performance"
    ]
    
    # 处理查询
    for query in queries:
        print(f"\n{'='*50}")
        print(f"用户查询: {query}")
        print('='*50)
        
        result = await agent.process_query(query)
        print(f"Agent回复:\n{result}")
        
        # 显示调试信息
        if agent.debug_manager.logs:
            print(f"\n调试信息 (最近3条):")
            for log in agent.debug_manager.logs[-3:]:
                print(f"  [{log['timestamp']}] {log['type']}: {str(log.get('tool_name', '')) or str(log.get('error', ''))[:50]}...")

if __name__ == "__main__":
    asyncio.run(main())