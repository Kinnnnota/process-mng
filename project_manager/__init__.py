"""
AI驱动的项目开发流程管理系统
支持Developer Mode和Reviewer Mode双模式管理
"""

__version__ = "1.0.0"
__author__ = "AI Project Manager"

from .project_manager import ProjectManager
from .review_engine import ReviewEngine
from .models import ProjectState, Phase, Mode

__all__ = ["ProjectManager", "ReviewEngine", "ProjectState", "Phase", "Mode"]
