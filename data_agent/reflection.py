from typing import List, Dict, Any, Optional
import json

class ReflectionEngine:
    """反思引擎，实现多轮反思和迭代优化能力"""
    
    def __init__(self, agent):
        self.agent = agent
        self.reflection_history: List[Dict[str, Any]] = []
    
    async def think_deeper(self, query: str, current_result: str, iterations: int = 1) -> str:
        """深度思考，进行多轮反思和优化"""
        # 检查agent是否为DataAnalysisAgent实例
        from data_agent.agent import DataAnalysisAgent
        if not isinstance(self.agent, DataAnalysisAgent):
            return current_result
            
        # 构建反思prompt
        reflection_prompt = self.agent.prompt_manager.get_prompt("reflection_analyzer")
        if not reflection_prompt:
            reflection_prompt = """你是一个AI反思专家。请对当前的分析结果进行深度思考和优化。

原始查询: {original_query}
当前结果: {current_result}

请执行以下反思和优化:
1. 分析当前结果的不足之处
2. 识别可能被忽略的要点
3. 提出改进建议
4. 如有必要，生成更深入的分析请求

请严格按照以下JSON格式返回结果，不要包含其他文字:
{
  "analysis": "当前结果的不足分析",
  "improvement_suggestions": ["建议1", "建议2"],
  "deep_analysis_needed": true,
  "new_query": "如果需要深入分析，请提供新的查询"
}"""

        # 进行多轮反思
        result = current_result
        for i in range(iterations):
            context = {
                "original_query": query,
                "current_result": result,
                "iteration": i + 1
            }
            
            # 调用LLM进行反思
            reflection_result = await self.agent._call_llm(reflection_prompt, context)
            
            # 记录反思历史
            self.reflection_history.append({
                "iteration": i + 1,
                "input": context,
                "output": reflection_result
            })
            
            # 解析反思结果
            if isinstance(reflection_result, dict):
                # 如果建议进行深入分析，则执行新查询
                if reflection_result.get("deep_analysis_needed", False) and reflection_result.get("new_query"):
                    new_query = reflection_result["new_query"]
                    result = await self.agent.process_query(new_query)
                else:
                    # 否则基于建议优化当前结果
                    suggestions = reflection_result.get("improvement_suggestions", [])
                    if suggestions:
                        # 构建优化prompt
                        optimization_prompt = """你是一个AI优化专家。请基于以下建议优化分析结果。

原始查询: {original_query}
当前结果: {current_result}
优化建议: {suggestions}

请提供优化后的结果，要求更加全面、准确和深入。"""
                        
                        optimization_context = {
                            "original_query": query,
                            "current_result": result,
                            "suggestions": suggestions
                        }
                        
                        result = await self.agent._call_llm(optimization_prompt, optimization_context)
            
            # 记录反思和优化过程
            self.agent.debug_manager.log_llm_input(f"反思迭代 {i+1}", context)
            self.agent.debug_manager.log_llm_output(json.dumps(reflection_result, ensure_ascii=False, indent=2))
        
        return result
    
    async def think_longer(self, query: str, time_allocation: int = 10) -> str:
        """长时间思考，分配更多时间进行深入分析"""
        # 检查agent是否为DataAnalysisAgent实例
        from data_agent.agent import DataAnalysisAgent
        if not isinstance(self.agent, DataAnalysisAgent):
            return f"长时间思考完成，原始查询: {query}"
            
        # 这里可以实现更复杂的时间分配策略
        # 例如，将时间分配给不同的分析阶段
        
        # 构建长时间思考prompt
        long_thinking_prompt = """你有更多时间来深入分析这个问题。请进行更全面、更细致的思考。

原始查询: {original_query}
思考时间: {time_allocation}分钟

请按照以下步骤进行深入分析:
1. 问题分解：将复杂问题拆分为多个子问题
2. 多角度分析：从不同维度审视问题
3. 数据验证：检查数据的准确性和完整性
4. 方案对比：比较不同解决方案的优劣
5. 风险评估：识别潜在风险和应对措施

请提供详细、深入的分析结果。"""
        
        context = {
            "original_query": query,
            "time_allocation": time_allocation
        }
        
        # 调用LLM进行长时间思考
        result = await self.agent._call_llm(long_thinking_prompt, context)
        
        # 记录思考过程
        self.agent.debug_manager.log_llm_input("长时间思考", context)
        self.agent.debug_manager.log_llm_output(json.dumps(result, ensure_ascii=False, indent=2))
        
        return result
    
    def get_reflection_history(self) -> List[Dict[str, Any]]:
        """获取反思历史"""
        return self.reflection_history
    
    def clear_reflection_history(self):
        """清空反思历史"""
        self.reflection_history.clear()
    
    async def compare_approaches(self, query: str, approaches: List[str]) -> str:
        """比较不同方法的优劣"""
        # 检查agent是否为DataAnalysisAgent实例
        from data_agent.agent import DataAnalysisAgent
        if not isinstance(self.agent, DataAnalysisAgent):
            return f"方法比较完成，原始查询: {query}"
            
        # 构建方法比较prompt
        comparison_prompt = """你是一个AI分析专家。请比较不同方法的优劣。

原始查询: {original_query}
待比较方法: {approaches}

请按照以下步骤进行分析:
1. 分析每种方法的适用场景
2. 比较每种方法的优缺点
3. 评估每种方法的风险
4. 给出推荐方案

请严格按照以下JSON格式返回结果:
{
  "approach_analysis": [
    {
      "approach": "方法1",
      "pros": ["优点1", "优点2"],
      "cons": ["缺点1", "缺点2"],
      "risk_assessment": "风险评估"
    }
  ],
  "recommendation": "推荐方案",
  "reasoning": "推荐理由"
}"""
        
        context = {
            "original_query": query,
            "approaches": approaches
        }
        
        # 调用LLM进行方法比较
        result = await self.agent._call_llm(comparison_prompt, context)
        
        # 记录比较过程
        self.agent.debug_manager.log_llm_input("方法比较", context)
        self.agent.debug_manager.log_llm_output(json.dumps(result, ensure_ascii=False, indent=2))
        
        return result