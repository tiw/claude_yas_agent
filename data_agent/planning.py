from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    """任务"""
    id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    estimated_duration: Optional[int] = None  # 预估执行时间（秒）
    priority: int = 1  # 优先级，1-5，5为最高优先级

class ProjectPlanner:
    """项目规划器，实现智能Planning能力"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_order: List[str] = []
    
    def add_task(self, task: Task):
        """添加任务"""
        self.tasks[task.id] = task
        self.task_order.append(task.id)
    
    def get_pending_tasks(self) -> List[Task]:
        """获取待处理任务"""
        return [
            task for task in self.tasks.values()
            if task.status == TaskStatus.PENDING
        ]
    
    def get_dependent_tasks(self, task_id: str) -> List[Task]:
        """获取依赖任务"""
        return [
            task for task in self.tasks.values()
            if task_id in task.dependencies
        ]
    
    def can_start_task(self, task_id: str) -> bool:
        """检查任务是否可以开始"""
        task = self.tasks[task_id]
        return all(
            self.tasks[dep_id].status == TaskStatus.COMPLETED
            for dep_id in task.dependencies
        )
    
    def start_task(self, task_id: str) -> bool:
        """开始任务"""
        task = self.tasks[task_id]
        if self.can_start_task(task_id):
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            return True
        return False
    
    def complete_task(self, task_id: str, result: Any = None):
        """完成任务"""
        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.result = result
    
    def fail_task(self, task_id: str, error: str):
        """任务失败"""
        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.error = error
        task.completed_at = datetime.now()
    
    def get_progress(self) -> Dict[str, int]:
        """获取进度"""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks.values() 
                       if task.status == TaskStatus.COMPLETED)
        failed = sum(1 for task in self.tasks.values() 
                    if task.status == TaskStatus.FAILED)
        in_progress = sum(1 for task in self.tasks.values() 
                         if task.status == TaskStatus.IN_PROGRESS)
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": total - completed - failed - in_progress
        }
    
    def get_task_by_priority(self) -> List[Task]:
        """按优先级获取任务列表"""
        tasks = list(self.tasks.values())
        return sorted(tasks, key=lambda x: x.priority, reverse=True)
    
    def estimate_project_duration(self) -> int:
        """预估项目总时长（秒）"""
        total_seconds = 0
        for task in self.tasks.values():
            if task.estimated_duration:
                total_seconds += task.estimated_duration
        return total_seconds
    
    def get_critical_path(self) -> List[str]:
        """获取关键路径（简化版）"""
        # 这里实现一个简化的关键路径算法
        # 实际项目中可能需要更复杂的算法
        critical_tasks = []
        for task_id in self.task_order:
            task = self.tasks[task_id]
            # 如果任务有依赖或者被其他任务依赖，则认为是关键任务
            if task.dependencies or self.get_dependent_tasks(task_id):
                critical_tasks.append(task_id)
        return critical_tasks