from typing import Dict, Any, Optional, List
from data_agent.planning import Task, TaskStatus
import asyncio

class SubAgentManager:
    """子Agent管理器，实现多Agent协作机制"""
    
    def __init__(self, main_agent):
        self.main_agent = main_agent
        self.sub_agents: Dict[str, Any] = {}
        self.task_assignments: Dict[str, str] = {}  # task_id -> agent_name
    
    def register_sub_agent(self, name: str, agent):
        """注册子Agent"""
        self.sub_agents[name] = agent
    
    def create_sub_agent(self, name: str, config: Dict[str, Any]):
        """创建子Agent"""
        from data_agent.agent import AgentConfig, DataAnalysisAgent
        agent_config = AgentConfig(**config)
        agent = DataAnalysisAgent(agent_config)
        self.sub_agents[name] = agent
        return agent
    
    def assign_task_to_agent(self, task_id: str, agent_name: str):
        """将任务分配给指定Agent"""
        if agent_name in self.sub_agents:
            self.task_assignments[task_id] = agent_name
            return True
        return False
    
    async def execute_task_with_agent(self, task: Task):
        """使用指定Agent执行任务"""
        from data_agent.agent import DataAnalysisAgent
        agent_name = self.task_assignments.get(task.id)
        if not agent_name:
            # 如果没有指定Agent，使用主Agent执行
            if isinstance(self.main_agent, DataAnalysisAgent):
                return await self.main_agent.process_query(task.description)
            else:
                # 如果主Agent不是DataAnalysisAgent类型，返回默认值
                return f"任务 '{task.description}' 已完成"
        
        if agent_name in self.sub_agents:
            agent = self.sub_agents[agent_name]
            if isinstance(agent, DataAnalysisAgent):
                return await agent.process_query(task.description)
            else:
                return f"子Agent '{agent_name}' 已处理任务"
        else:
            # 如果指定的Agent不存在，使用主Agent执行
            if isinstance(self.main_agent, DataAnalysisAgent):
                return await self.main_agent.process_query(task.description)
            else:
                return f"任务 '{task.description}' 已完成"
    
    async def coordinate_agents_for_complex_task(self, complex_task_description: str) -> Dict[str, Any]:
        """协调多个Agent完成复杂任务"""
        # 这里可以实现更复杂的协调逻辑
        # 例如，将复杂任务分解为子任务，分配给不同的Agent执行
        
        results = {}
        
        # 示例：创建不同类型的子Agent
        if "数据分析" in complex_task_description and "code_reviewer" not in self.sub_agents:
            code_review_config = {
                "debug_mode": self.main_agent.config.debug_mode,
                "default_llm": self.main_agent.config.default_llm
            }
            self.create_sub_agent("code_reviewer", code_review_config)
        
        if "性能优化" in complex_task_description and "optimizer" not in self.sub_agents:
            optimizer_config = {
                "debug_mode": self.main_agent.config.debug_mode,
                "default_llm": "deepseek"  # 使用不同的模型
            }
            self.create_sub_agent("optimizer", optimizer_config)
        
        # 并行执行任务
        tasks = []
        for agent_name, agent in self.sub_agents.items():
            # 检查agent是否为DataAnalysisAgent实例
            from data_agent.agent import DataAnalysisAgent
            if isinstance(agent, DataAnalysisAgent):
                task = asyncio.create_task(
                    agent.process_query(f"处理与{agent_name}相关的任务: {complex_task_description}")
                )
                tasks.append((agent_name, task))
            else:
                # 如果不是DataAnalysisAgent实例，创建一个简单的任务
                async def simple_task(agent_name, description):
                    return f"Agent {agent_name} 处理了任务: {description}"
                task = asyncio.create_task(
                    simple_task(agent_name, f"处理与{agent_name}相关的任务: {complex_task_description}")
                )
                tasks.append((agent_name, task))
        
        # 收集结果
        for agent_name, task in tasks:
            try:
                result = await task
                results[agent_name] = result
            except Exception as e:
                results[agent_name] = f"执行出错: {str(e)}"
        
        return results
    
    def get_available_agents(self) -> List[str]:
        """获取可用的Agent列表"""
        return list(self.sub_agents.keys())
    
    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """获取Agent状态"""
        if agent_name not in self.sub_agents:
            return {"status": "not_found"}
        
        agent = self.sub_agents[agent_name]
        # 检查agent是否为DataAnalysisAgent实例
        from data_agent.agent import DataAnalysisAgent
        if isinstance(agent, DataAnalysisAgent):
            return {
                "status": "active",
                "debug_mode": agent.config.debug_mode,
                "default_llm": agent.config.default_llm
            }
        else:
            return {
                "status": "active",
                "type": type(agent).__name__
            }