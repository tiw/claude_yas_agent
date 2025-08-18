from typing import Dict, Any, Optional, List
from data_agent.planning import Task, TaskStatus
from enum import Enum
import asyncio


class AgentType(Enum):
    """Agent类型枚举"""
    DATA_ANALYSIS = "data_analysis"  # 数据分析Agent
    INVESTMENT = "investment"        # 投资分析Agent
    DEMAND_NETWORK = "demand_network"  # 需求网络分析Agent
    CUSTOM = "custom"                # 自定义Agent

class SubAgentManager:
    """子Agent管理器，实现多Agent协作机制"""
    
    def __init__(self, main_agent):
        self.main_agent = main_agent
        self.sub_agents: Dict[str, Any] = {}
        self.agent_types: Dict[str, AgentType] = {}  # agent_name -> agent_type
        self.task_assignments: Dict[str, str] = {}  # task_id -> agent_name
        self.current_agent = "main"  # 当前使用的Agent
    
    def register_sub_agent(self, name: str, agent, agent_type: AgentType = AgentType.CUSTOM):
        """注册子Agent"""
        self.sub_agents[name] = agent
        self.agent_types[name] = agent_type
    
    def create_sub_agent(self, name: str, config: Dict[str, Any], agent_type: AgentType = AgentType.DATA_ANALYSIS):
        """创建子Agent"""
        agent = None
        if agent_type == AgentType.DATA_ANALYSIS:
            from data_agent.agent import AgentConfig, DataAnalysisAgent
            agent_config = AgentConfig(**config)
            agent = DataAnalysisAgent(agent_config)
        elif agent_type == AgentType.DEMAND_NETWORK:
            from data_agent.demand_network_agent import DemandNetworkAgentConfig, DemandNetworkAnalysisAgent
            agent_config = DemandNetworkAgentConfig(**config)
            agent = DemandNetworkAnalysisAgent(agent_config)
        elif agent_type == AgentType.INVESTMENT:
            # 可以添加投资分析Agent
            from data_agent.agent import AgentConfig, DataAnalysisAgent
            agent_config = AgentConfig(**config)
            agent = DataAnalysisAgent(agent_config)
        else:
            # 默认使用数据分析Agent
            from data_agent.agent import AgentConfig, DataAnalysisAgent
            agent_config = AgentConfig(**config)
            agent = DataAnalysisAgent(agent_config)
            
        if agent:
            self.sub_agents[name] = agent
            self.agent_types[name] = agent_type
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
        from data_agent.demand_network_agent import DemandNetworkAnalysisAgent
        
        agent_name = self.task_assignments.get(task.id)
        if not agent_name:
            # 如果没有指定Agent，使用当前选择的Agent执行
            return await self.execute_with_current_agent(task.description)
        
        if agent_name in self.sub_agents:
            agent = self.sub_agents[agent_name]
            # 根据Agent类型调用相应的方法
            if isinstance(agent, DataAnalysisAgent):
                return await agent.process_query(task.description)
            elif isinstance(agent, DemandNetworkAnalysisAgent):
                return await agent.process_query(task.description)
            else:
                return f"子Agent '{agent_name}' 已处理任务"
        else:
            # 如果指定的Agent不存在，使用当前选择的Agent执行
            return await self.execute_with_current_agent(task.description)
    
    async def execute_with_current_agent(self, query: str, files: list = None):
        """使用当前选择的Agent执行查询"""
        from data_agent.agent import DataAnalysisAgent
        from data_agent.demand_network_agent import DemandNetworkAnalysisAgent
        
        # 如果当前选择的是主Agent
        if self.current_agent == "main":
            if isinstance(self.main_agent, DataAnalysisAgent):
                return await self.main_agent.process_query(query, files=files)
            else:
                return f"主Agent已处理查询: {query}"
        
        # 如果当前选择的是子Agent
        if self.current_agent in self.sub_agents:
            agent = self.sub_agents[self.current_agent]
            # 根据Agent类型调用相应的方法
            if isinstance(agent, DataAnalysisAgent):
                return await agent.process_query(query, files=files)
            elif isinstance(agent, DemandNetworkAnalysisAgent):
                return await agent.process_query(query, files=files)
            else:
                return f"Agent '{self.current_agent}' 已处理查询: {query}"
        else:
            # 如果当前选择的Agent不存在，使用主Agent执行
            if isinstance(self.main_agent, DataAnalysisAgent):
                return await self.main_agent.process_query(query, files=files)
            else:
                return f"主Agent已处理查询: {query}"
    
    def switch_agent(self, agent_name: str) -> bool:
        """切换当前使用的Agent"""
        if agent_name == "main":
            self.current_agent = "main"
            return True
        elif agent_name in self.sub_agents:
            self.current_agent = agent_name
            return True
        return False
    
    def get_current_agent_info(self) -> Dict[str, Any]:
        """获取当前Agent信息"""
        if self.current_agent == "main":
            return {
                "name": "main",
                "type": "data_analysis",
                "description": "数据分析Agent"
            }
        elif self.current_agent in self.sub_agents:
            agent_type = self.agent_types.get(self.current_agent, AgentType.CUSTOM)
            descriptions = {
                AgentType.DATA_ANALYSIS: "数据分析Agent",
                AgentType.INVESTMENT: "投资分析Agent",
                AgentType.DEMAND_NETWORK: "需求网络分析Agent",
                AgentType.CUSTOM: "自定义Agent"
            }
            return {
                "name": self.current_agent,
                "type": agent_type.value,
                "description": descriptions.get(agent_type, "未知Agent")
            }
        else:
            return {
                "name": "unknown",
                "type": "unknown",
                "description": "未知Agent"
            }
    
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