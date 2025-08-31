# AI驱动的项目开发流程管理系统

一个支持双模式（Developer Mode 和 Reviewer Mode）的AI驱动项目开发流程管理系统，通过循环迭代的方式管理五个开发阶段：基本设计、详细设计、开发实现、单元测试、集成测试。系统支持完全自动化的开发流程，最小化手动干预。

## 🚀 系统特性

- **双模式管理**：支持开发模式和评审模式的智能切换
- **五阶段流程**：BASIC_DESIGN → DETAIL_DESIGN → DEVELOPMENT → UNIT_TEST → INTEGRATION_TEST 的完整开发流程
- **智能评审**：基于规则的自动评审和评分系统（25分制）
- **自动化工作流**：支持完全自动化的开发流程，AI自动推进项目进度
- **防死循环**：内置迭代限制和强制转换机制
- **状态持久化**：项目状态自动保存和恢复
- **报告生成**：自动生成项目进度和质量报告
- **智能回退**：自动检测Critical问题并回退到合适阶段
- **要件定义**：支持自然语言描述项目技术栈和配置

## 📋 系统要求

- Python 3.7+
- 标准库（无需额外依赖）

## 🛠️ 安装和使用

### 1. 克隆项目
```bash
git clone <repository-url>
cd process-mng
```

### 2. 运行系统

#### 演示模式
```bash
python main.py demo
```

#### 要件定义（新功能）
```bash
# 定义项目要件（使用自然语言描述）
python main.py define --project "我的项目" --requirements "使用Python和Django开发Web应用，使用PostgreSQL数据库，部署到AWS"

# 查看项目要件配置
python main.py requirements --project "我的项目"
```

#### 完全自动化工作流（推荐）
```bash
# 标准自动化工作流
python main.py auto --project "我的项目"

# 智能工作流（达到目标分数后自动进入下一阶段）
python main.py smart --project "我的项目" --score 85.0

# 持续改进工作流（在通过后继续优化）
python main.py improve --project "我的项目" --phases 5
```

#### 手动模式（传统方式）
```bash
# 初始化项目
python main.py init --project "我的项目"

# 开发模式
python main.py dev --project "我的项目" --phase current

# 评审模式
python main.py review --project "我的项目" --phase current

# 查看状态
python main.py status --project "我的项目"

# 生成报告
python main.py report --project "我的项目"
```

## 📖 使用指南

### 自动化工作流（推荐）

#### 1. 完全自动化开发
```python
from project_manager.auto_workflow import AutoWorkflow

# 创建自动化工作流
auto_workflow = AutoWorkflow("我的项目")

# 运行完全自动化工作流
result = auto_workflow.run_auto_workflow()
print(f"工作流状态：{result['status']}")
print(f"完成阶段数：{len(result['phases_completed'])}")
```

#### 2. 智能工作流
```python
# 设置目标分数，AI会自动优化直到达到目标
result = auto_workflow.run_smart_workflow(target_score=85.0)
```

#### 3. 持续改进工作流
```python
# 在达到通过分数后继续改进
result = auto_workflow.run_continuous_improvement(max_phases=5)
```

### 手动工作流程

1. **初始化项目**
   ```python
   from project_manager import ProjectManager
   manager = ProjectManager("my_project")
   ```

2. **开发模式工作**
   ```python
   # 切换到开发模式
   manager.set_mode("developer")
   
   # 执行当前阶段任务
   result = manager.execute_phase()
   print(result)
   ```

3. **评审模式工作**
   ```python
   # 切换到评审模式
   manager.set_mode("reviewer")
   
   # 评审当前阶段成果
   review_result = manager.review_phase()
   print(f"评分：{review_result['score']}分")
   ```

4. **阶段转换**
   ```python
   # 检查是否可以进入下一阶段
   if manager.check_phase_transition():
       print("可以进入下一阶段")
   else:
       print("需要继续迭代")
   
   # 强制进入下一阶段
   manager.force_next_phase()
   ```

### 阶段说明

#### BASIC_DESIGN 阶段
- **专注目标**：业务逻辑、系统架构、数据库设计、外部接口
- **必需输出**：业务流程图、系统架构图、ER图、API清单
- **评审权重**：业务完整性(30%)、数据库设计(25%)、架构合理性(25%)、接口定义(20%)
- **通过分数**：80分
- **最大迭代**：5次
- **回退触发**：数据库设计无法支持、架构存在根本缺陷

#### DETAIL_DESIGN 阶段
- **专注目标**：代码架构、算法设计、数据结构、类设计
- **必需输出**：类图、算法伪代码、数据结构定义、时序图
- **评审权重**：类设计(30%)、数据结构(25%)、算法合理性(25%)、模块耦合(20%)
- **通过分数**：80分
- **最大迭代**：4次
- **回退触发**：数据库设计无法支持、架构存在根本缺陷

#### DEVELOPMENT 阶段
- **专注目标**：功能实现、代码质量、异常处理、性能优化
- **必需输出**：源代码、配置文件、数据库脚本、README
- **评审权重**：功能完整性(35%)、代码规范(25%)、异常处理(20%)、性能(20%)
- **通过分数**：85分
- **最大迭代**：4次
- **回退触发**：数据结构无法实现、算法逻辑漏洞

#### UNIT_TEST 阶段
- **专注目标**：单元测试覆盖、边界测试、异常测试
- **必需输出**：测试用例、测试代码、覆盖率报告
- **评审权重**：覆盖率(35%)、边界测试(30%)、异常测试(35%)
- **通过分数**：90分
- **最大迭代**：3次
- **回退触发**：核心功能测试失败、设计缺陷

#### INTEGRATION_TEST 阶段
- **专注目标**：系统集成、端到端测试、性能测试
- **必需输出**：集成测试用例、性能报告、部署文档
- **评审权重**：集成完整性(40%)、性能达标(30%)、稳定性(30%)
- **通过分数**：95分
- **最大迭代**：3次

### 问题分级

- **Critical（严重）**：必须修复，影响核心功能或安全性，可能触发回退
- **Major（主要）**：应该修复，影响功能正确性或用户体验
- **Minor（次要）**：建议改进，提升代码质量或性能

## 📁 项目结构

```
process-mng/
├── main.py                    # 主程序入口
├── config.yaml               # 配置文件
├── requirements.txt          # 依赖文件
├── README.md                 # 项目说明
├── ai_development_guide.md   # AI开发指南
├── ai_usage_examples.md      # 使用示例
├── .cursorrules              # Cursor规则
├── .cursor/                  # Cursor配置
└── project_manager/          # 核心模块
    ├── __init__.py
    ├── project_manager.py    # 项目管理器
    ├── models.py             # 数据模型
    ├── review_engine.py      # 评审引擎
    ├── auto_workflow.py      # 自动化工作流
    ├── ai_integration.py     # AI集成
    └── prompts/              # 提示词模板
        ├── developer_mode.md
        └── reviewer_mode.md
```

## 🔧 核心API

### ProjectManager 类

```python
class ProjectManager:
    def __init__(self, project_name: str)
    def set_mode(self, mode: str)  # "developer" or "reviewer"
    def execute_phase(self) -> str  # 执行当前阶段任务
    def review_phase(self) -> dict  # 返回评分和建议
    def check_phase_transition(self) -> bool  # 判断是否可以进入下一阶段
    def force_next_phase(self)  # 强制进入下一阶段
    def rollback_to_phase(self, target_phase: Phase, reason: str)  # 回退到指定阶段
    def check_rollback_needed(self) -> Optional[Phase]  # 检查是否需要回退
    def get_current_status(self) -> dict  # 获取当前项目状态
    def export_report(self) -> str  # 导出项目报告
```

### AutoWorkflow 类

```python
class AutoWorkflow:
    def __init__(self, project_name: str, auto_mode: bool = True)
    def run_auto_workflow(self) -> dict  # 运行完全自动化工作流
    def run_smart_workflow(self, target_score: float) -> dict  # 运行智能工作流
    def run_continuous_improvement(self, max_phases: int) -> dict  # 运行持续改进工作流
    def get_workflow_status(self) -> dict  # 获取工作流状态
```

### RequirementsEngine 类

```python
class RequirementsEngine:
    def parse_requirements(self, natural_language: str) -> dict  # 解析自然语言描述
    def generate_config_files(self, requirements: dict, project_name: str) -> dict  # 生成配置文件
```

### ReviewEngine 类

```python
class ReviewEngine:
    def evaluate(self, phase: str, content: str) -> dict  # 评估内容
    def get_critical_issues(self) -> list  # 获取Critical问题
    def get_next_improvement(self) -> str  # 获取最重要的改进点
    def calculate_score(self, checklist: dict) -> float  # 计算总分
```

## 📊 示例输出

### 自动化工作流状态
```
🤖 开始自动化工作流：我的项目
🔄 自动模式：启用

🔄 第 1 次自动迭代
📍 当前阶段：BASIC_DESIGN
📊 当前评分：None

🎨 执行阶段：BASIC_DESIGN
   📝 开发模式：生成内容...
   ✅ 开发完成：基本设计文档已生成：project_manager/我的项目/phase_outputs/basic_design/basic_design_v1.md
   🔍 评审模式：评估内容...
   📊 评审完成：82.5分

✅ 阶段 BASIC_DESIGN 完成，准备进入下一阶段
```

### 项目状态
```
📊 项目状态：my_project
📍 当前阶段：BASIC_DESIGN
🔄 迭代次数：1
🎯 当前模式：developer
📈 项目状态：IN_PROGRESS
⭐ 最新评分：82.5分
🚫 阻塞问题：0个
💡 改进建议：3个
📝 评审次数：2次
⚠️  来自回退：否
🔄 回退次数：0次
🔒 质量门禁：{'allow_rollback': True, 'max_rollbacks_per_phase': 2, 'total_rollbacks': 0, 'force_forward_threshold': 3}
```

### 评审结果
```json
{
  "score": 82.5,
  "issues": [
    {
      "level": "MINOR",
      "description": "建议增加接口定义"
    }
  ],
  "improvements": [
    "建议增加接口定义"
  ],
  "checklist": {
    "业务完整性": 30.0,
    "数据库设计": 25.0,
    "架构合理性": 25.0,
    "接口定义": 20.0
  }
}
```

## 🎯 最佳实践

### 自动化工作流（推荐）
1. **优先使用自动化工作流**：减少手动干预，提高效率
2. **选择合适的自动化模式**：
   - 标准自动化：适合一般项目
   - 智能自动化：适合有明确质量要求的项目
   - 持续改进：适合追求高质量的项目
3. **设置合理的参数**：目标分数、最大迭代次数、最大阶段数
4. **监控工作流状态**：定期检查进度，及时处理异常

### 开发模式
1. 根据提示词模板生成高质量内容
2. 确保覆盖所有检查项要求
3. 关注代码规范和最佳实践
4. 添加充分的注释和文档

### 评审模式
1. 客观公正地进行评估
2. 重点关注Critical和Bug级别问题
3. 每次只关注一个最重要的改进点
4. 提供具体、可操作的改进建议

### 项目管理
1. 定期检查项目状态
2. 及时处理阻塞问题
3. 合理使用强制转换机制
4. 定期导出项目报告

## 🐛 故障排除

### 常见问题

1. **项目初始化失败**
   - 检查项目名称是否包含特殊字符
   - 确保有足够的磁盘空间
   - 检查文件权限

2. **评审失败**
   - 确保当前模式为reviewer
   - 检查阶段输出文件是否存在
   - 验证文件编码格式

3. **阶段转换失败**
   - 检查是否达到通过条件
   - 查看评审历史记录
   - 考虑使用强制转换

4. **自动化工作流卡住**
   - 检查是否达到最大迭代次数
   - 查看是否有Critical问题需要手动处理
   - 检查项目状态文件是否损坏

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
manager = ProjectManager("debug_project")
```

## 📝 更新日志

### v1.2.0
- 新增要件定义功能
- 支持自然语言描述项目技术栈
- 自动生成配置文件
- 完善项目文档

### v1.1.0
- 新增自动化工作流功能
- 支持智能工作流和持续改进工作流
- 优化项目文档和示例
- 清理不相关文件

### v1.0.0
- 初始版本发布
- 支持双模式管理
- 实现五阶段流程
- 内置评审引擎
- 提供命令行界面

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件
- 参与讨论

---

**注意**：本系统支持完全自动化的开发流程，推荐使用自动化工作流来最大化减少手动干预。
