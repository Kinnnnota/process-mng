"""
项目数据模型定义
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
import json
from datetime import datetime


class Phase(Enum):
    """项目阶段枚举（简化版 - 仅包含核心开发阶段）"""
    BASIC_DESIGN = "BASIC_DESIGN"
    DETAIL_DESIGN = "DETAIL_DESIGN"
    DEVELOPMENT = "DEVELOPMENT"
    # UNIT_TEST 和 INTEGRATION_TEST 已移除 - 留待人工确认


class Mode(Enum):
    """系统模式枚举"""
    DEVELOPER = "developer"
    REVIEWER = "reviewer"


class IssueLevel(Enum):
    """问题级别枚举"""
    CRITICAL = "CRITICAL"  # 需回退
    MAJOR = "MAJOR"        # 必须修复
    MINOR = "MINOR"        # 建议改进


@dataclass
class Issue:
    """问题数据结构"""
    level: IssueLevel
    description: str
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'level': self.level.value,
            'description': self.description,
            'line_number': self.line_number,
            'file_path': self.file_path,
            'created_at': self.created_at
        }


@dataclass
class ReviewResult:
    """评审结果数据结构"""
    score: float
    issues: List[Issue]
    improvements: List[str]
    checklist: Dict[str, float]
    review_date: str = None
    phase: str = None
    iteration: int = 0
    
    def __post_init__(self):
        if self.review_date is None:
            self.review_date = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'score': self.score,
            'issues': [issue.to_dict() for issue in self.issues],
            'improvements': self.improvements,
            'checklist': self.checklist,
            'review_date': self.review_date,
            'phase': self.phase,
            'iteration': self.iteration
        }


@dataclass
class PhaseHistory:
    """阶段历史记录"""
    iterations: int = 0
    scores: List[float] = field(default_factory=list)
    issues_fixed: List[str] = field(default_factory=list)
    rollback_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'iterations': self.iterations,
            'scores': self.scores,
            'issues_fixed': self.issues_fixed,
            'rollback_count': self.rollback_count
        }


@dataclass
class TechStack:
    """技术栈配置"""
    language: str
    framework: Optional[str] = None
    frontend: Optional[str] = None
    backend: Optional[str] = None
    database: Optional[str] = None
    cache: Optional[str] = None
    message_queue: Optional[str] = None
    monitoring: Optional[str] = None
    testing: Optional[str] = None
    deployment: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'language': self.language,
            'framework': self.framework,
            'frontend': self.frontend,
            'backend': self.backend,
            'database': self.database,
            'cache': self.cache,
            'message_queue': self.message_queue,
            'monitoring': self.monitoring,
            'testing': self.testing,
            'deployment': self.deployment
        }


@dataclass
class DatabaseConfig:
    """数据库配置"""
    type: str
    host: str = 'localhost'
    port: int = 5432
    name: str = 'app_db'
    user: str = 'app_user'
    password: str = ''
    connection_pool: bool = True
    migrations: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'host': self.host,
            'port': self.port,
            'name': self.name,
            'user': self.user,
            'password': self.password,
            'connection_pool': self.connection_pool,
            'migrations': self.migrations
        }


@dataclass
class DeploymentConfig:
    """部署配置"""
    platform: str = 'local'
    containerization: bool = False
    orchestration: bool = False
    auto_scaling: bool = False
    load_balancer: bool = False
    ssl: bool = False
    domain: str = ''
    environment: str = 'development'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'platform': self.platform,
            'containerization': self.containerization,
            'orchestration': self.orchestration,
            'auto_scaling': self.auto_scaling,
            'load_balancer': self.load_balancer,
            'ssl': self.ssl,
            'domain': self.domain,
            'environment': self.environment
        }


@dataclass
class PerformanceConfig:
    """性能配置"""
    response_time: str = 'normal'  # normal, fast, ultra_fast
    concurrent_users: int = 100
    data_volume: str = 'small'  # small, medium, large
    availability: float = 99.9
    caching: bool = False
    cdn: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'response_time': self.response_time,
            'concurrent_users': self.concurrent_users,
            'data_volume': self.data_volume,
            'availability': self.availability,
            'caching': self.caching,
            'cdn': self.cdn
        }


@dataclass
class ProjectRequirements:
    """项目要件配置"""
    project_info: Dict[str, Any]
    tech_stack: TechStack
    project_type: str
    database: DatabaseConfig
    deployment: DeploymentConfig
    performance: PerformanceConfig
    development_config: Dict[str, Any]
    deployment_config: Dict[str, Any]
    database_config: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'project_info': self.project_info,
            'tech_stack': self.tech_stack.to_dict(),
            'project_type': self.project_type,
            'database': self.database.to_dict(),
            'deployment': self.deployment.to_dict(),
            'performance': self.performance.to_dict(),
            'development_config': self.development_config,
            'deployment_config': self.deployment_config,
            'database_config': self.database_config
        }


@dataclass
class ProjectState:
    """项目状态数据结构 (不包含issue - issue存储在文件中)"""
    project_name: str
    current_phase: Phase
    phase_iteration: int
    current_mode: Mode
    status: str  # READY_FOR_REVIEW, IN_PROGRESS, COMPLETED
    phase_scores: List[float]
    # blocked_issues 已移除 - 使用 IssueStorage 从文件读取
    improvements: List[str]
    review_history: List[ReviewResult]
    created_at: str
    updated_at: str = None
    from_rollback: bool = False
    rollback_reason: str = ""
    rollback_count: int = 0
    phase_history: Dict[str, PhaseHistory] = field(default_factory=dict)
    quality_gates: Dict[str, Any] = field(default_factory=lambda: {
        "allow_rollback": True,
        "max_rollbacks_per_phase": 2,
        "total_rollbacks": 0,
        "force_forward_threshold": 3
    })
    requirements: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        
        # 初始化阶段历史
        if not self.phase_history:
            for phase in Phase:
                self.phase_history[phase.value] = PhaseHistory()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式 (不包含blocked_issues - 存储在文件中)"""
        data = asdict(self)
        data['current_phase'] = self.current_phase.value
        data['current_mode'] = self.current_mode.value
        data['phase_scores'] = self.phase_scores
        # blocked_issues 已移除 - 从 IssueStorage 读取
        data['review_history'] = [result.to_dict() for result in self.review_history]
        data['phase_history'] = {k: v.to_dict() for k, v in self.phase_history.items()}
        data['quality_gates'] = self.quality_gates
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectState':
        """从字典创建实例 (兼容旧数据,忽略blocked_issues字段)"""
        # 转换枚举类型
        data['current_phase'] = Phase(data['current_phase'])
        data['current_mode'] = Mode(data['current_mode'])

        # 移除 blocked_issues 字段(如果存在,用于兼容旧数据)
        data.pop('blocked_issues', None)
        
        # 转换评审历史
        data['review_history'] = [
            ReviewResult(
                score=result['score'],
                issues=[
                    Issue(
                        level=IssueLevel(issue['level']),
                        description=issue['description'],
                        line_number=issue.get('line_number'),
                        file_path=issue.get('file_path'),
                        created_at=issue.get('created_at')
                    ) for issue in result.get('issues', [])
                ],
                improvements=result.get('improvements', []),
                checklist=result.get('checklist', {}),
                review_date=result.get('review_date'),
                phase=result.get('phase'),
                iteration=result.get('iteration', 0)
            ) for result in data.get('review_history', [])
        ]
        
        # 转换阶段历史
        phase_history = {}
        for phase_name, history_data in data.get('phase_history', {}).items():
            phase_history[phase_name] = PhaseHistory(
                iterations=history_data.get('iterations', 0),
                scores=history_data.get('scores', []),
                issues_fixed=history_data.get('issues_fixed', []),
                rollback_count=history_data.get('rollback_count', 0)
            )
        data['phase_history'] = phase_history
        
        # 确保quality_gates存在
        if 'quality_gates' not in data:
            data['quality_gates'] = {
                "allow_rollback": True,
                "max_rollbacks_per_phase": 2,
                "total_rollbacks": 0,
                "force_forward_threshold": 3
            }
        
        return cls(**data)


class PhaseConfig:
    """阶段配置类"""
    
    @staticmethod
    def get_basic_design_checklist() -> Dict[str, float]:
        """获取基本设计阶段检查项"""
        return {
            "业务完整性": 30.0,
            "数据库设计": 25.0,
            "架构合理性": 25.0,
            "接口定义": 20.0
        }
    
    @staticmethod
    def get_detail_design_checklist() -> Dict[str, float]:
        """获取详细设计阶段检查项"""
        return {
            "类设计": 30.0,
            "数据结构": 25.0,
            "算法合理性": 25.0,
            "模块耦合": 20.0
        }
    
    @staticmethod
    def get_development_checklist() -> Dict[str, float]:
        """获取开发实现阶段检查项"""
        return {
            "功能完整性": 35.0,
            "代码规范": 25.0,
            "异常处理": 20.0,
            "性能": 20.0
        }
    
    @staticmethod
    def get_checklist_for_phase(phase: Phase) -> Dict[str, float]:
        """获取指定阶段的检查项（仅核心开发阶段）"""
        checklists = {
            Phase.BASIC_DESIGN: PhaseConfig.get_basic_design_checklist(),
            Phase.DETAIL_DESIGN: PhaseConfig.get_detail_design_checklist(),
            Phase.DEVELOPMENT: PhaseConfig.get_development_checklist()
        }
        return checklists.get(phase, {})
    
    @staticmethod
    def get_max_iterations(phase: Phase) -> int:
        """获取阶段最大迭代次数（仅核心开发阶段）"""
        max_iterations = {
            Phase.BASIC_DESIGN: 5,
            Phase.DETAIL_DESIGN: 4,
            Phase.DEVELOPMENT: 4
        }
        return max_iterations.get(phase, 3)

    @staticmethod
    def get_pass_threshold(phase: Phase) -> float:
        """获取阶段通过阈值（仅核心开发阶段）"""
        thresholds = {
            Phase.BASIC_DESIGN: 80.0,
            Phase.DETAIL_DESIGN: 80.0,
            Phase.DEVELOPMENT: 85.0
        }
        return thresholds.get(phase, 80.0)
    
    @staticmethod
    def get_phase_output_format(phase: Phase) -> str:
        """获取阶段输出格式要求（仅核心开发阶段）"""
        formats = {
            Phase.BASIC_DESIGN: """
输出要求：
- 业务流程图（mermaid格式）
- 系统架构图
- 数据库ER图和表结构
- API接口清单
- 技术选型说明
禁止：不涉及代码细节、算法实现、性能优化
            """,
            Phase.DETAIL_DESIGN: """
输出要求：
- 类图（含方法签名）
- 核心算法伪代码
- 数据结构定义
- 关键流程时序图
- 异常处理策略
禁止：不涉及具体代码语法、测试用例
            """,
            Phase.DEVELOPMENT: """
输出要求：
- 完整源代码
- 配置文件
- 数据库脚本
- README文档
禁止：不涉及测试细节、部署配置
            """
        }
        return formats.get(phase, "")
    
    @staticmethod
    def can_rollback_to(phase: Phase) -> List[Phase]:
        """获取可以回退到的阶段（仅核心开发阶段）"""
        rollback_rules = {
            Phase.DETAIL_DESIGN: [Phase.BASIC_DESIGN],
            Phase.DEVELOPMENT: [Phase.DETAIL_DESIGN]
        }
        return rollback_rules.get(phase, [])
    
    @staticmethod
    def get_rollback_conditions(phase: Phase) -> List[str]:
        """获取回退触发条件（仅核心开发阶段）"""
        conditions = {
            Phase.DETAIL_DESIGN: [
                "数据库设计无法支持",
                "架构存在根本缺陷"
            ],
            Phase.DEVELOPMENT: [
                "数据结构无法实现",
                "算法逻辑漏洞"
            ]
        }
        return conditions.get(phase, [])
