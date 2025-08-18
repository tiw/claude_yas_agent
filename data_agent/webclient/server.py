#!/usr/bin/env python3
"""
Web服务后端
为数据分析Agent提供Web API接口
"""

import asyncio
import os
import sys
from typing import Dict, Any
import json
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from aiohttp import web, WSMsgType
from data_agent.agent import DataAnalysisAgent, AgentConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebService:
    """Web服务类"""
    
    def __init__(self):
        self.app = web.Application()
        self.agent = None
        
    def setup_routes(self):
        """设置路由"""
        # 页面路由
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/debug-monitor.html', self.debug_monitor)
        
        # API路由
        self.app.router.add_post('/api/chat', self.chat)
        self.app.router.add_post('/api/upload', self.upload_file)
        self.app.router.add_get('/api/health', self.health_check)
        self.app.router.add_get('/api/status', self.system_status)
        self.app.router.add_get('/api/mcp/status', self.mcp_status)
        self.app.router.add_get('/api/debug/logs', self.get_debug_logs)
        self.app.router.add_get('/api/debug/logs/{session_id}', self.get_debug_logs_by_session)
        self.app.router.add_get('/api/debug/sessions', self.get_debug_sessions)
        self.app.router.add_post('/api/debug/clear', self.clear_debug_logs)
        
        # WebSocket路由
        self.app.router.add_get('/api/ws', self.websocket_handler)
    
    async def initialize_agent(self):
        """初始化数据分析Agent"""
        try:
            config = AgentConfig(
                debug_mode=True,
                langfuse_enabled=False,
                default_llm="qwen"  # 默认使用Qwen
            )
            self.agent = DataAnalysisAgent(config)
            logger.info("数据分析Agent初始化成功")
        except Exception as e:
            logger.error(f"初始化数据分析Agent失败: {e}")
            self.agent = None
    
    async def index(self, request):
        """主页"""
        # 读取并返回index.html
        index_path = os.path.join(os.path.dirname(__file__), 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        else:
            return web.Response(text="Welcome to Data Analysis Agent API", content_type='text/plain')
    
    async def debug_monitor(self, request):
        """调试监控页面"""
        # 读取并返回debug_monitor.html
        debug_path = os.path.join(os.path.dirname(__file__), 'debug_monitor.html')
        if os.path.exists(debug_path):
            with open(debug_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        else:
            return web.Response(text="Debug monitor page not found", content_type='text/plain')
    
    async def health_check(self, request):
        """健康检查"""
        return web.json_response({
            "status": "healthy",
            "service": "data-analysis-agent-web",
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def system_status(self, request):
        """系统状态检查"""
        try:
            if not self.agent:
                await self.initialize_agent()
                if not self.agent:
                    return web.json_response({
                        "status": "error",
                        "message": "Agent初始化失败"
                    }, status=500)
            
            # 检查Agent组件状态
            status_info = {
                "status": "running",
                "components": {
                    "agent": "initialized",
                    "mcp_client": "available" if self.agent.mcp_client else "unavailable",
                    "llm_manager": "available" if self.agent.llm_manager else "unavailable",
                    "debug_manager": "available" if self.agent.debug_manager else "unavailable",
                    "prompt_manager": "available" if self.agent.prompt_manager else "unavailable"
                },
                "configuration": {
                    "debug_mode": self.agent.config.debug_mode,
                    "default_llm": self.agent.config.default_llm,
                    "langfuse_enabled": self.agent.config.langfuse_enabled
                }
            }
            
            # 如果MCP客户端可用，检查服务器状态
            if self.agent.mcp_client:
                status_info["mcp_servers"] = {}
                for server_name, server_info in self.agent.mcp_client.server_info.items():
                    status_info["mcp_servers"][server_name] = {
                        "url": server_info.get("url"),
                        "healthy": server_info.get("healthy", False),
                        "instructions": server_info.get("instructions", "")
                    }
            
            return web.json_response(status_info)
            
        except Exception as e:
            logger.error(f"获取系统状态时出错: {e}")
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=500)
    
    async def mcp_status(self, request):
        """MCP状态检查"""
        try:
            if not self.agent:
                await self.initialize_agent()
                if not self.agent:
                    return web.json_response({
                        "status": "error",
                        "message": "Agent初始化失败"
                    }, status=500)
            
            if not self.agent.mcp_client:
                return web.json_response({
                    "status": "error",
                    "message": "MCP客户端未初始化"
                }, status=500)
            
            # 获取MCP服务器状态
            mcp_status = {
                "status": "success",
                "servers": {},
                "available_tools": self.agent.mcp_client.get_available_tools()
            }
            
            for server_name, server_info in self.agent.mcp_client.server_info.items():
                mcp_status["servers"][server_name] = {
                    "url": server_info.get("url"),
                    "healthy": server_info.get("healthy", False),
                    "instructions": server_info.get("instructions", ""),
                    "tools": []  # 可以扩展为从服务器动态获取工具列表
                }
            
            # 统计信息
            mcp_status["summary"] = {
                "total_servers": len(mcp_status["servers"]),
                "healthy_servers": len([s for s in mcp_status["servers"].values() if s["healthy"]]),
                "available_tools": len(mcp_status["available_tools"])
            }
            
            return web.json_response(mcp_status)
            
        except Exception as e:
            logger.error(f"获取MCP状态时出错: {e}")
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=500)
    
    async def get_debug_logs(self, request):
        """获取调试日志"""
        try:
            if not self.agent or not self.agent.debug_manager:
                return web.json_response({
                    "logs": [],
                    "status": "success"
                })
            
            logs = self.agent.debug_manager.get_logs()
            return web.json_response({
                "logs": logs,
                "status": "success"
            })
        except Exception as e:
            logger.error(f"获取调试日志时出错: {e}")
            return web.json_response({
                "error": str(e),
                "status": "error"
            }, status=500)
            
    async def get_debug_logs_by_session(self, request):
        """按会话ID获取调试日志"""
        try:
            session_id = request.match_info.get('session_id')
            if not session_id:
                return web.json_response({
                    "error": "缺少会话ID",
                    "status": "error"
                }, status=400)
                
            if not self.agent or not self.agent.debug_manager:
                return web.json_response({
                    "logs": [],
                    "status": "success"
                })
            
            logs = self.agent.debug_manager.get_logs(session_id)
            return web.json_response({
                "logs": logs,
                "session_id": session_id,
                "status": "success"
            })
        except Exception as e:
            logger.error(f"按会话ID获取调试日志时出错: {e}")
            return web.json_response({
                "error": str(e),
                "status": "error"
            }, status=500)
            
    async def get_debug_sessions(self, request):
        """获取所有调试会话"""
        try:
            if not self.agent or not self.agent.debug_manager:
                return web.json_response({
                    "sessions": [],
                    "status": "success"
                })
            
            sessions = self.agent.debug_manager.get_sessions()
            return web.json_response({
                "sessions": sessions,
                "status": "success"
            })
        except Exception as e:
            logger.error(f"获取调试会话时出错: {e}")
            return web.json_response({
                "error": str(e),
                "status": "error"
            }, status=500)
    
    async def clear_debug_logs(self, request):
        """清空调试日志"""
        try:
            if self.agent and self.agent.debug_manager:
                self.agent.debug_manager.clear_logs()
            
            return web.json_response({
                "message": "调试日志已清空",
                "status": "success"
            })
        except Exception as e:
            logger.error(f"清空调试日志时出错: {e}")
            return web.json_response({
                "error": str(e),
                "status": "error"
            }, status=500)
    
    async def upload_file(self, request):
        """处理文件上传"""
        try:
            # 获取上传的文件
            reader = await request.multipart()
            
            # 存储文件内容和元数据
            uploaded_files = []
            
            # 创建临时目录存储上传的文件
            upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # 处理每个上传的文件
            while True:
                part = await reader.next()
                if part is None:
                    break
                
                if part.name == 'files':
                    filename = part.filename
                    if not filename:
                        continue
                        
                    # 生成安全的文件名
                    import uuid
                    safe_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(upload_dir, safe_filename)
                    
                    # 保存文件
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = await part.read_chunk()
                            if not chunk:
                                break
                            f.write(chunk)
                    
                    # 获取文件信息
                    file_size = os.path.getsize(file_path)
                    
                    # 读取文件内容（仅对小文件）
                    file_content = None
                    if file_size < 1024 * 1024:  # 小于1MB的文件读取内容
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            file_content = f.read()
                    
                    uploaded_files.append({
                        "filename": filename,
                        "safe_filename": safe_filename,
                        "file_path": file_path,
                        "size": file_size,
                        "content": file_content
                    })
            
            return web.json_response({
                "message": f"成功上传 {len(uploaded_files)} 个文件",
                "files": uploaded_files,
                "status": "success"
            })
            
        except Exception as e:
            logger.error(f"处理文件上传时出错: {e}")
            return web.json_response({
                "error": str(e),
                "status": "error"
            }, status=500)
    
    async def chat(self, request):
        """处理聊天请求"""
        try:
            # 解析请求数据
            data = await request.json()
            message = data.get('message', '')
            files = data.get('files', [])
            agent_type = data.get('agent', 'main')  # 获取请求的Agent类型
            
            if not message and not files:
                return web.json_response({
                    "error": "消息或文件不能为空"
                }, status=400)
            
            if not self.agent:
                await self.initialize_agent()
                if not self.agent:
                    return web.json_response({
                        "error": "Agent初始化失败"
                    }, status=500)
            
            # 如果有上传的文件，将文件信息添加到消息中
            if files:
                file_info = "\n\n上传的文件信息:\n"
                for file in files:
                    file_info += f"- 文件名: {file['filename']}\n"
                    if file.get('content'):
                        file_info += f"  文件内容预览: {file['content'][:500]}...\n"
                    else:
                        file_info += f"  文件路径: {file['file_path']}\n"
                
                message += file_info
            
            # 根据请求的Agent类型处理消息
            logger.info(f"处理用户消息: {message} (使用Agent: {agent_type})")
            
            if agent_type == 'main':
                # 使用主Agent处理
                response = await self.agent.process_query(message, files=files)
            elif agent_type == 'demand-network':
                # 创建或使用需求网络分析Agent
                if not hasattr(self, 'demand_network_agent') or self.demand_network_agent is None:
                    # 创建需求网络分析Agent
                    from data_agent.demand_network_agent import DemandNetworkAgentConfig, DemandNetworkAnalysisAgent
                    config = DemandNetworkAgentConfig(
                        debug_mode=self.agent.config.debug_mode,
                        langfuse_enabled=self.agent.config.langfuse_enabled,
                        default_llm=self.agent.config.default_llm
                    )
                    self.demand_network_agent = DemandNetworkAnalysisAgent(config)
                
                # 使用需求网络分析Agent处理
                response = await self.demand_network_agent.process_query(message, files=files)
            else:
                # 默认使用主Agent处理
                response = await self.agent.process_query(message, files=files)
            
            return web.json_response({
                "response": response,
                "status": "success"
            })
            
        except Exception as e:
            logger.error(f"处理聊天请求时出错: {e}")
            return web.json_response({
                "error": str(e),
                "status": "error"
            }, status=500)
    
    async def websocket_handler(self, request):
        """WebSocket处理函数"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # 初始化Agent（如果还没有）
        if not self.agent:
            await self.initialize_agent()
        
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    try:
                        # 解析消息
                        data = json.loads(msg.data)
                        message = data.get('message', '')
                        
                        if message and self.agent:
                            # 获取会话ID（如果提供）
                            session_id = data.get('session_id')
                            agent_type = data.get('agent', 'main')  # 获取请求的Agent类型
                            
                            # 如果有会话ID，启动该会话
                            if session_id:
                                self.agent.enhanced_memory.start_session(session_id)
                            else:
                                # 否则开始新会话
                                session_id = self.agent.enhanced_memory.start_session()
                            
                            # 根据请求的Agent类型处理消息
                            if agent_type == 'main':
                                # 使用主Agent处理
                                response = await self.agent.process_query(message)
                            elif agent_type == 'demand-network':
                                # 创建或使用需求网络分析Agent
                                if not hasattr(self, 'demand_network_agent') or self.demand_network_agent is None:
                                    # 创建需求网络分析Agent
                                    from data_agent.demand_network_agent import DemandNetworkAgentConfig, DemandNetworkAnalysisAgent
                                    config = DemandNetworkAgentConfig(
                                        debug_mode=self.agent.config.debug_mode,
                                        langfuse_enabled=self.agent.config.langfuse_enabled,
                                        default_llm=self.agent.config.default_llm
                                    )
                                    self.demand_network_agent = DemandNetworkAnalysisAgent(config)
                                
                                # 使用需求网络分析Agent处理
                                response = await self.demand_network_agent.process_query(message)
                            else:
                                # 默认使用主Agent处理
                                response = await self.agent.process_query(message)
                            
                            # 获取当前会话ID
                            session_id = self.agent.debug_manager.current_session_id if self.agent.debug_manager else session_id
                            
                            # 发送响应，包含会话ID
                            await ws.send_json({
                                "response": response,
                                "session_id": session_id,
                                "status": "success"
                            })
                            
                            # 发送当前会话的调试日志
                            if self.agent.debug_manager and session_id:
                                session_logs = self.agent.debug_manager.get_logs(session_id)
                                if session_logs:
                                    await ws.send_json({
                                        "debug_logs": session_logs,
                                        "session_id": session_id,
                                        "type": "debug_update",
                                        "status": "success"
                                    })
                        else:
                            await ws.send_json({
                                "error": "消息为空或Agent未初始化",
                                "status": "error"
                            })
                    except Exception as e:
                        logger.error(f"处理WebSocket消息时出错: {e}")
                        await ws.send_json({
                            "error": str(e),
                            "status": "error"
                        })
            elif msg.type == WSMsgType.ERROR:
                logger.error(f'WebSocket连接错误: {ws.exception()}')
        
        return ws
    
    def run(self, host='localhost', port=8084):
        """启动Web服务"""
        # 设置路由
        self.setup_routes()
        
        # 初始化Agent
        async def init_agent(app):
            await self.initialize_agent()
        
        self.app.on_startup.append(init_agent)
        
        # 启动服务
        web.run_app(self.app, host=host, port=port)

def main():
    """主函数"""
    service = WebService()
    print(f"正在启动Web服务...")
    print(f"访问地址: http://localhost:8084")
    print(f"WebSocket地址: ws://localhost:8084/api/ws")
    service.run()

if __name__ == "__main__":
    main()