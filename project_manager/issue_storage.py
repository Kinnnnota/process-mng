"""
Issue存储模块
负责将issue持久化到文件系统,实现黑箱评审
"""
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .models import Issue, IssueLevel, Phase


class IssueStorage:
    """Issue文件存储管理器"""

    def __init__(self, project_dir: Path):
        """
        初始化Issue存储管理器

        Args:
            project_dir: 项目根目录
        """
        self.project_dir = project_dir
        self.issues_dir = project_dir / "issues"
        self.blocked_issues_file = self.issues_dir / "blocked_issues.json"

        # 确保目录存在
        self.issues_dir.mkdir(parents=True, exist_ok=True)

    def save_review_issues(
        self,
        phase: Phase,
        iteration: int,
        issues: List[Issue]
    ) -> None:
        """
        保存某次评审的所有issue到文件

        Args:
            phase: 评审阶段
            iteration: 迭代次数
            issues: issue列表
        """
        filename = f"{phase.value.lower()}_iter_{iteration}_issues.json"
        filepath = self.issues_dir / filename

        # 将Issue对象转换为字典
        issues_data = {
            "phase": phase.value,
            "iteration": iteration,
            "review_date": datetime.now().isoformat(),
            "issues": [self._issue_to_dict(issue) for issue in issues]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(issues_data, f, ensure_ascii=False, indent=2)

    def load_review_issues(
        self,
        phase: Phase,
        iteration: int
    ) -> List[Issue]:
        """
        加载某次评审的issue

        Args:
            phase: 评审阶段
            iteration: 迭代次数

        Returns:
            issue列表
        """
        filename = f"{phase.value.lower()}_iter_{iteration}_issues.json"
        filepath = self.issues_dir / filename

        if not filepath.exists():
            return []

        with open(filepath, 'r', encoding='utf-8') as f:
            issues_data = json.load(f)

        return [self._dict_to_issue(issue_dict) for issue_dict in issues_data.get("issues", [])]

    def save_blocked_issues(self, issues: List[Issue]) -> None:
        """
        保存当前所有阻塞的issue

        Args:
            issues: 阻塞issue列表
        """
        blocked_data = {
            "updated_at": datetime.now().isoformat(),
            "count": len(issues),
            "issues": [self._issue_to_dict(issue) for issue in issues]
        }

        with open(self.blocked_issues_file, 'w', encoding='utf-8') as f:
            json.dump(blocked_data, f, ensure_ascii=False, indent=2)

    def load_blocked_issues(self) -> List[Issue]:
        """
        加载当前所有阻塞的issue

        Returns:
            阻塞issue列表
        """
        if not self.blocked_issues_file.exists():
            return []

        with open(self.blocked_issues_file, 'r', encoding='utf-8') as f:
            blocked_data = json.load(f)

        return [self._dict_to_issue(issue_dict) for issue_dict in blocked_data.get("issues", [])]

    def get_blocked_issues_count(self) -> int:
        """
        获取当前阻塞issue数量

        Returns:
            阻塞issue数量
        """
        if not self.blocked_issues_file.exists():
            return 0

        with open(self.blocked_issues_file, 'r', encoding='utf-8') as f:
            blocked_data = json.load(f)

        return blocked_data.get("count", 0)

    def add_blocked_issues(self, new_issues: List[Issue]) -> None:
        """
        添加新的阻塞issue(追加到现有列表)

        Args:
            new_issues: 新的阻塞issue列表
        """
        # 加载现有的阻塞issue
        existing_issues = self.load_blocked_issues()

        # 合并(去重:基于description和level)
        existing_keys = {(issue.description, issue.level.value) for issue in existing_issues}

        for issue in new_issues:
            key = (issue.description, issue.level.value)
            if key not in existing_keys:
                existing_issues.append(issue)
                existing_keys.add(key)

        # 保存合并后的列表
        self.save_blocked_issues(existing_issues)

    def clear_blocked_issues(self) -> None:
        """清空所有阻塞issue"""
        self.save_blocked_issues([])

    def get_all_issues_for_phase(self, phase: Phase) -> List[Issue]:
        """
        获取某阶段所有迭代的issue

        Args:
            phase: 评审阶段

        Returns:
            该阶段所有issue列表
        """
        all_issues = []

        # 遍历issues目录,找到所有该阶段的issue文件
        pattern = f"{phase.value.lower()}_iter_*_issues.json"
        for filepath in self.issues_dir.glob(pattern):
            with open(filepath, 'r', encoding='utf-8') as f:
                issues_data = json.load(f)

            issues = [self._dict_to_issue(issue_dict) for issue_dict in issues_data.get("issues", [])]
            all_issues.extend(issues)

        return all_issues

    def get_latest_issues_for_phase(self, phase: Phase) -> Optional[List[Issue]]:
        """
        获取某阶段最新一次评审的issue

        Args:
            phase: 评审阶段

        Returns:
            最新的issue列表,如果没有则返回None
        """
        # 找到所有该阶段的issue文件
        pattern = f"{phase.value.lower()}_iter_*_issues.json"
        files = list(self.issues_dir.glob(pattern))

        if not files:
            return None

        # 找到最新的文件(根据iteration号)
        latest_file = max(files, key=lambda f: self._extract_iteration(f.name))

        with open(latest_file, 'r', encoding='utf-8') as f:
            issues_data = json.load(f)

        return [self._dict_to_issue(issue_dict) for issue_dict in issues_data.get("issues", [])]

    def _extract_iteration(self, filename: str) -> int:
        """从文件名提取迭代次数"""
        import re
        match = re.search(r'iter_(\d+)_', filename)
        return int(match.group(1)) if match else 0

    def _issue_to_dict(self, issue: Issue) -> Dict[str, Any]:
        """将Issue对象转换为字典"""
        return {
            "level": issue.level.value,
            "description": issue.description,
            "line_number": issue.line_number,
            "file_path": issue.file_path,
            "created_at": issue.created_at
        }

    def _dict_to_issue(self, issue_dict: Dict[str, Any]) -> Issue:
        """将字典转换为Issue对象"""
        return Issue(
            level=IssueLevel(issue_dict["level"]),
            description=issue_dict["description"],
            line_number=issue_dict.get("line_number"),
            file_path=issue_dict.get("file_path"),
            created_at=issue_dict.get("created_at", datetime.now().isoformat())
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取issue统计信息

        Returns:
            统计信息字典
        """
        stats = {
            "total_blocked": self.get_blocked_issues_count(),
            "by_phase": {}
        }

        # 统计各阶段的issue
        for phase in Phase:
            issues = self.get_all_issues_for_phase(phase)
            stats["by_phase"][phase.value] = {
                "total": len(issues),
                "critical": len([i for i in issues if i.level == IssueLevel.CRITICAL]),
                "major": len([i for i in issues if i.level == IssueLevel.MAJOR]),
                "minor": len([i for i in issues if i.level == IssueLevel.MINOR])
            }

        return stats
