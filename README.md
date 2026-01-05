# AI驱动的项目开发流程管理系统

一个支持双模式（Developer Mode 和 Reviewer Mode）的AI驱动项目开发流程管理系统，通过循环迭代的方式管理五个开发阶段，采用**黑箱评审机制**确保每次评审的独立性。

## 🚀 核心特性

- **双模式管理** - 支持开发模式和评审模式的智能切换
- **五阶段流程** - BASIC_DESIGN → DETAIL_DESIGN → DEVELOPMENT → UNIT_TEST → INTEGRATION_TEST
- **黑箱评审** - 每次评审完全独立，不保留历史记忆
- **智能评分** - 基于规则的自动评审和评分系统（100分制）
- **Issue文件化** - 所有问题存储在文件中，支持追溯和分析
- **状态持久化** - 项目状态自动保存和恢复

## 🎯 黑箱评审机制

### 核心设计
1. **无状态评审引擎** - ReviewEngine完全无状态，每次评审都是独立过程
2. **文件持久化** - 所有Issue存储在文件中，不依赖内存
3. **完全隔离** - 评审时只能看到当前阶段输出，看不到历史评审

### Issue存储结构
```
project_manager/{project_name}/
  ├── issues/
  │   ├── basic_design_iter_1_issues.json    # 每次评审的issue
  │   ├── development_iter_1_issues.json
  │   └── blocked_issues.json                # 当前阻塞issue
  ├── phase_outputs/                         # 各阶段输出
  ├── project_state.json                     # 项目状态
  └── review_history.md                      # 评审历史
```

## 📋 系统要求

- Python 3.7+
- 标准库（无需额外依赖）

## 🛠️ 快速开始

### 基本使用

```python
from project_manager import ProjectManager

# 1. 初始化项目
pm = ProjectManager("my_project")

# 2. 开发模式
pm.set_mode("developer")
result = pm.execute_phase()

# 3. 评审模式（黑箱评审）
pm.set_mode("reviewer")
review = pm.review_phase()
print(f"评分: {review['score']}分")
print(f"发现问题: {len(review['issues'])}个")

# 4. 获取阻塞Issue
blocked_issues = pm.get_blocked_issues()
print(f"阻塞问题: {len(blocked_issues)}个")
```

### Issue管理

```python
# 获取某阶段某次迭代的issue
from project_manager.models import Phase

issues = pm.issue_storage.load_review_issues(
    phase=Phase.DEVELOPMENT,
    iteration=1
)

# 获取某阶段所有issue
all_issues = pm.issue_storage.get_all_issues_for_phase(Phase.DEVELOPMENT)

# 获取统计信息
stats = pm.issue_storage.get_statistics()
print(stats)

# 清空阻塞issue
pm.clear_blocked_issues()
```

## 📁 项目结构

```
process-mng/
├── main.py                       # 主程序入口
├── README.md                     # 项目说明
└── project_manager/              # 核心模块
    ├── project_manager.py        # 项目管理器
    ├── models.py                 # 数据模型
    ├── review_engine.py          # 评审引擎（无状态）
    ├── issue_storage.py          # Issue文件存储管理器
    ├── ai_integration.py         # AI集成
    ├── prompt_manager.py         # 提示词管理器
    └── prompts/                  # 提示词模板
        ├── standards/            # 评审标准
        ├── templates/            # 生成模板
        └── configs/              # 阶段配置
```

## 🔧 核心API

### ProjectManager
```python
class ProjectManager:
    def __init__(self, project_name: str)
    def set_mode(self, mode: str)                    # "developer" or "reviewer"
    def execute_phase(self) -> str                   # 执行当前阶段
    def review_phase(self) -> dict                   # 黑箱评审
    def get_blocked_issues(self) -> List[Issue]      # 获取阻塞issue
    def clear_blocked_issues(self) -> None           # 清空阻塞issue
    def get_current_status(self) -> dict             # 获取项目状态
```

### IssueStorage
```python
class IssueStorage:
    def save_review_issues(phase, iteration, issues) # 保存评审issue
    def load_review_issues(phase, iteration)         # 加载评审issue
    def save_blocked_issues(issues)                  # 保存阻塞issue
    def load_blocked_issues(self)                    # 加载阻塞issue
    def get_blocked_issues_count(self)               # 获取阻塞数量
    def get_statistics(self)                         # 获取统计信息
```

### ReviewEngine（无状态）
```python
class ReviewEngine:
    def evaluate(phase, content, file_path) -> dict  # 黑箱评审

    # 静态方法
    @staticmethod
    def get_critical_issues(issues)                  # 获取Critical问题
    @staticmethod
    def generate_formatted_review_report(...)        # 生成评审报告
    @staticmethod
    def generate_detailed_analysis(issue, content)   # 生成详细分析
```

## 📊 评审阶段

### BASIC_DESIGN（基本设计）- 100分制
- **业务完整性**: 30分
- **数据库设计**: 25分
- **架构合理性**: 25分
- **接口定义**: 20分
- **通过分数**: 80分

### DETAIL_DESIGN（详细设计）- 100分制
- **类设计**: 30分
- **数据结构**: 25分
- **算法合理性**: 25分
- **模块耦合**: 20分
- **通过分数**: 80分

### DEVELOPMENT（开发实现）- 100分制
- **功能完整性**: 35分
- **代码规范**: 25分
- **异常处理**: 20分
- **性能**: 20分
- **通过分数**: 85分

### UNIT_TEST（单元测试）- 100分制
- **覆盖率**: 35分
- **边界测试**: 30分
- **异常测试**: 35分
- **通过分数**: 90分

### INTEGRATION_TEST（集成测试）- 100分制
- **集成完整性**: 40分
- **性能达标**: 30分
- **稳定性**: 30分
- **通过分数**: 95分

## 🎯 Issue级别

- **CRITICAL** - 需要回退到前一阶段
- **MAJOR** - 必须修复才能继续
- **MINOR** - 建议改进，不阻塞流程

## 🔄 黑箱评审优势

1. **评审一致性** - 相同内容的评审结果完全一致
2. **无历史干扰** - 每次评审基于当前代码，不受历史影响
3. **可追溯性** - 所有issue文件化，可随时查看历史
4. **数据安全** - 项目状态和issue分离存储，更安全
5. **易于分析** - 文件化存储便于统计分析

## 📝 更新日志

### v2.0.0 - 黑箱评审架构
- 重构ReviewEngine为完全无状态
- 新增IssueStorage文件存储管理器
- ProjectState移除blocked_issues字段
- 实现真正的黑箱评审机制

### v1.2.0
- 新增要件定义功能
- 支持自然语言描述项目技术栈

### v1.0.0
- 初始版本发布
- 支持双模式管理
- 实现五阶段流程

## 📄 许可证

MIT License
