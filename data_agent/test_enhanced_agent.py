#!/usr/bin/env python3
"""
测试增强版Agent功能
验证借鉴Claude Code的Agent增强能力
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_agent.agent import DataAnalysisAgent, AgentConfig
from data_agent.planning import Task, TaskStatus
from data_agent.memory import MemoryManager

async def test_enhanced_agent():
    """测试增强版Agent功能"""
    print("开始测试增强版Agent功能...")
    
    # 配置Agent
    config = AgentConfig(
        debug_mode=True,
        langfuse_enabled=False,
        default_llm="qwen"
    )
    
    # 创建Agent实例
    agent = DataAnalysisAgent(config)
    
    print("\n1. 测试多层级内存管理机制")
    # 测试内存管理
    agent.memory.set_memory("user_memory", "user_preference", "喜欢深度分析")
    agent.memory.set_memory("project_memory", "project_name", "数据分析项目")
    
    user_pref = agent.memory.get_memory("user_memory", "user_preference")
    project_info = agent.memory.get_memory("project_memory", "project_name")
    
    print(f"  用户偏好: {user_pref}")
    print(f"  项目信息: {project_info}")
    
    print("\n2. 测试智能Planning能力")
    # 创建任务
    task1 = Task(
        id="task1",
        name="数据收集",
        description="收集苹果公司财务数据",
        priority=3,
        estimated_duration=30
    )
    
    task2 = Task(
        id="task2",
        name="数据分析",
        description="分析收集到的财务数据",
        dependencies=["task1"],
        priority=4,
        estimated_duration=60
    )
    
    task3 = Task(
        id="task3",
        name="生成报告",
        description="生成分析报告",
        dependencies=["task2"],
        priority=5,
        estimated_duration=45
    )
    
    # 添加任务到规划器
    agent.planner.add_task(task1)
    agent.planner.add_task(task2)
    agent.planner.add_task(task3)
    
    # 查看任务状态
    pending_tasks = agent.planner.get_pending_tasks()
    print(f"  待处理任务数量: {len(pending_tasks)}")
    
    # 查看项目进度
    progress = agent.planner.get_progress()
    print(f"  项目进度: {progress}")
    
    # 查看关键路径
    critical_path = agent.planner.get_critical_path()
    print(f"  关键路径: {critical_path}")
    
    print("\n3. 测试多Agent协作机制")
    # 查看可用Agent
    available_agents = agent.sub_agent_manager.get_available_agents()
    print(f"  可用Agent: {available_agents}")
    
    # 创建子Agent
    reviewer_config = {
        "debug_mode": True,
        "default_llm": "qwen"
    }
    reviewer_agent = agent.sub_agent_manager.create_sub_agent("data_reviewer", reviewer_config)
    
    optimizer_config = {
        "debug_mode": True,
        "default_llm": "deepseek"
    }
    optimizer_agent = agent.sub_agent_manager.create_sub_agent("performance_optimizer", optimizer_config)
    
    # 查看更新后的可用Agent
    updated_agents = agent.sub_agent_manager.get_available_agents()
    print(f"  创建子Agent后可用Agent: {updated_agents}")
    
    print("\n4. 测试多轮反思和迭代优化能力")
    # 简单查询测试反思能力
    query = "分析苹果公司最近一季度的财务表现"
    result = await agent.process_query(query)
    
    print(f"  初始分析结果: {type(result)}")
    
    # 进行深度思考
    if hasattr(agent, 'reflection_engine'):
        deep_result = await agent.reflection_engine.think_deeper(query, str(result), iterations=1)
        print(f"  深度思考后结果: {type(deep_result)}")
    
    print("\n5. 测试MCP工具调用")
    # 测试实际的MCP工具调用
    mcp_result = await agent.process_query("查询苹果公司最近一季度的营收数据")
    print(f"  MCP工具调用结果: {type(mcp_result)}")
    
    print("\n6. 测试CLI工具")
    # 测试CLI命令（通过模拟）
    cli_result = await agent.process_query("比较苹果和微软最近一季度的财务数据")
    print(f"  CLI模拟查询结果: {type(cli_result)}")
    
    print("\n所有增强功能测试完成!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_agent())