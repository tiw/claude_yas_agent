#!/usr/bin/env python3
"""
测试继承关系
"""

import asyncio
from data_agent.agent import AgentConfig, DataAnalysisAgent
from data_agent.demand_network_agent import DemandNetworkAgentConfig, DemandNetworkAnalysisAgent


async def test_inheritance():
    """测试继承关系"""
    print("测试继承关系...")
    
    # 创建主Agent
    config = AgentConfig(debug_mode=True)
    main_agent = DataAnalysisAgent(config)
    
    # 检查继承关系
    print(f"主Agent类型: {type(main_agent)}")
    print(f"主Agent是否是BaseAgent的实例: {isinstance(main_agent, DataAnalysisAgent)}")
    
    # 创建需求网络分析Agent
    demand_config = DemandNetworkAgentConfig(debug_mode=True)
    demand_agent = DemandNetworkAnalysisAgent(demand_config)
    
    # 检查继承关系
    print(f"需求网络分析Agent类型: {type(demand_agent)}")
    print(f"需求网络分析Agent是否是BaseAgent的实例: {isinstance(demand_agent, DemandNetworkAnalysisAgent)}")
    
    # 检查共享的组件
    print("\n共享组件检查:")
    print(f"主Agent有debug_manager: {hasattr(main_agent, 'debug_manager')}")
    print(f"主Agent有prompt_manager: {hasattr(main_agent, 'prompt_manager')}")
    print(f"主Agent有enhanced_memory: {hasattr(main_agent, 'enhanced_memory')}")
    print(f"主Agent有reflection_engine: {hasattr(main_agent, 'reflection_engine')}")
    
    print(f"需求网络分析Agent有debug_manager: {hasattr(demand_agent, 'debug_manager')}")
    print(f"需求网络分析Agent有prompt_manager: {hasattr(demand_agent, 'prompt_manager')}")
    print(f"需求网络分析Agent有enhanced_memory: {hasattr(demand_agent, 'enhanced_memory')}")
    print(f"需求网络分析Agent有reflection_engine: {hasattr(demand_agent, 'reflection_engine')}")
    
    print("\n测试完成!")


if __name__ == "__main__":
    asyncio.run(test_inheritance())