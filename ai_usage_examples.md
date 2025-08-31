# Cursor AI 使用示例

## 概述
本文档展示如何在Cursor中使用AI功能，严格按照项目管理模板进行开发。系统支持完全自动化的开发流程，最小化手动干预。

## 使用方法

### 1. 基本使用流程

#### 1.1 创建AI指令
```python
from project_manager.ai_integration import create_ai_instruction

# 创建AI指令
instruction = create_ai_instruction("my_project", "请为项目添加核心功能模块")
print(instruction)
```

#### 1.2 验证AI输出
```python
from project_manager.ai_integration import validate_and_update

# 验证AI输出并更新项目状态
result = validate_and_update("my_project", ai_output_content)
print(f"验证结果：{result}")
```

### 2. 在Cursor中的具体操作

#### 2.1 开发新功能
当你在Cursor中需要开发新功能时：

1. **打开AI助手**：按 `Ctrl+K` 或点击AI助手按钮

2. **输入指令**：
```
请按照项目管理模板为项目"my_project"添加核心功能模块
```

3. **AI会生成指令**：
```python
# AI会读取项目状态并生成详细指令
from project_manager.ai_integration import create_ai_instruction

instruction = create_ai_instruction("my_project", "添加核心功能模块")
print(instruction)
```

4. **AI会按照模板生成代码**：
```python
# 根据当前阶段生成相应的代码
# 如果是BASIC_DESIGN阶段，会生成设计文档
# 如果是DEVELOPMENT阶段，会生成实现代码
```

#### 2.2 代码评审
当需要评审代码时：

1. **输入评审指令**：
```
请按照项目管理模板评审当前项目的代码实现
```

2. **AI会执行评审**：
```python
from project_manager import ProjectManager

manager = ProjectManager("my_project")
manager.set_mode("reviewer")
review_result = manager.review_phase()
print(f"评审结果：{review_result}")
```

### 3. 自动化工作流（强烈推荐）

#### 3.1 完全自动化开发
现在系统支持完全自动化的开发流程，无需手动切换模式：

```bash
# 运行完全自动化工作流
python main.py auto --project "我的项目"
```

这个命令会：
1. 自动在开发模式和评审模式之间切换
2. 自动推进项目阶段
3. 自动处理迭代和改进
4. 最小化手动干预

#### 3.2 智能工作流
设置目标分数，AI会自动优化直到达到目标：

```bash
# 运行智能工作流，目标分数85分
python main.py smart --project "我的项目" --score 85.0
```

#### 3.3 持续改进工作流
在达到通过分数后继续改进：

```bash
# 运行持续改进工作流
python main.py improve --project "我的项目" --phases 5
```

#### 3.4 在Cursor中使用自动化工作流
在Cursor中，您可以这样使用：

```
用户：请为项目"我的项目"运行自动化开发流程

AI行为：
1. 检查项目状态
2. 自动执行开发模式生成内容
3. 自动切换到评审模式评估内容
4. 根据评分自动决定是否进入下一阶段
5. 自动处理迭代和改进
6. 生成最终报告
```

### 4. 实际使用场景

#### 4.1 场景1：开始新项目
```
用户：请帮我创建一个新的项目管理系统

AI行为：
1. 检查项目状态（新项目）
2. 设置当前阶段为BASIC_DESIGN
3. 读取设计阶段提示词模板
4. 生成基本设计文档
5. 更新项目状态
```

#### 4.2 场景2：开发功能模块
```
用户：请为项目添加核心功能模块

AI行为：
1. 检查当前项目状态和阶段
2. 读取对应阶段的提示词模板
3. 生成符合要求的代码
4. 确保代码质量和规范性
5. 添加必要的测试用例
6. 更新项目状态
```

#### 4.3 场景3：代码评审
```
用户：请评审当前的核心功能模块

AI行为：
1. 读取当前阶段的输出文件
2. 按照评审标准进行评估
3. 生成详细的评审报告
4. 提供具体的改进建议
5. 更新项目评分和状态
```

#### 4.4 场景4：自动化开发（强烈推荐）
```
用户：请为项目"我的项目"运行自动化开发流程

AI行为：
1. 启动自动化工作流
2. 自动在开发模式和评审模式间切换
3. 自动推进项目阶段
4. 自动处理迭代和改进
5. 生成完整的项目报告
```

### 5. 配置文件的作用

#### 5.1 `.cursorrules` 文件
这个文件告诉Cursor AI：
- 项目的整体架构和流程
- 代码质量要求
- 文件组织规范
- 评审标准

#### 5.2 `.cursor/ai_config.json` 文件
这个文件定义了：
- 项目的具体配置
- 各阶段的要求和权重
- AI的行为规则

#### 5.3 `ai_development_guide.md` 文件
这个文件提供了：
- 详细的开发指导
- 最佳实践
- 使用示例

### 6. 高级使用技巧

#### 6.1 自定义提示词
你可以修改 `project_manager/prompts/` 目录下的提示词文件，定制AI的行为：

```markdown
# 在 developer_mode.md 中添加自定义要求
## 自定义要求
- 必须使用特定的设计模式
- 必须遵循特定的编码规范
- 必须包含特定的测试框架
```

#### 6.2 调整评审标准
你可以修改 `config.yaml` 文件，调整评审标准：

```yaml
phases:
  BASIC_DESIGN:
    review_weights:
      业务完整性: 35  # 调整权重
      数据库设计: 20
      架构合理性: 25
      接口定义: 20
    pass_score: 85  # 调整通过分数
```

#### 6.3 集成外部工具
你可以扩展 `ai_integration.py`，集成外部工具：

```python
def integrate_external_tools(self, output: str) -> str:
    """集成外部工具"""
    # 集成代码格式化工具
    output = self._format_code(output)
    
    # 集成代码检查工具
    output = self._lint_code(output)
    
    # 集成测试工具
    output = self._run_tests(output)
    
    return output
```

### 7. 自动化工作流详解

#### 7.1 自动化工作流类型

**1. 标准自动化工作流**
```python
from project_manager.auto_workflow import AutoWorkflow

# 创建自动化工作流
auto_workflow = AutoWorkflow("my_project")

# 运行自动化工作流
result = auto_workflow.run_auto_workflow()
print(f"工作流状态：{result['status']}")
print(f"完成阶段数：{len(result['phases_completed'])}")
```

**2. 智能工作流**
```python
# 设置目标分数，AI会自动优化
result = auto_workflow.run_smart_workflow(target_score=85.0)
```

**3. 持续改进工作流**
```python
# 在达到通过分数后继续改进
result = auto_workflow.run_continuous_improvement(max_phases=5)
```

#### 7.2 自动化工作流特性

- **自动模式切换**：无需手动在开发模式和评审模式间切换
- **自动阶段推进**：根据评分自动决定是否进入下一阶段
- **自动迭代处理**：自动处理迭代和改进
- **自动回退机制**：检测到Critical问题时自动回退
- **智能优化**：根据评审结果自动优化内容

#### 7.3 自动化工作流配置

```python
# 自定义自动化工作流参数
auto_workflow = AutoWorkflow("my_project", auto_mode=True)
auto_workflow.max_auto_iterations = 15  # 设置最大迭代次数

# 运行自定义工作流
result = auto_workflow.run_auto_workflow()
```

### 8. 故障排除

#### 8.1 常见问题

**问题1：AI不按照模板生成代码**
- 检查 `.cursorrules` 文件是否正确配置
- 确保提示词文件存在且格式正确
- 验证项目状态文件是否完整

**问题2：评审结果不符合预期**
- 检查 `config.yaml` 中的评审权重配置
- 确保评审标准文件格式正确
- 验证输出文件是否完整

**问题3：项目状态不同步**
- 检查状态文件的读写权限
- 确保状态更新逻辑正确
- 验证文件路径是否正确

**问题4：自动化工作流卡住**
- 检查是否达到最大迭代次数
- 查看是否有Critical问题需要手动处理
- 检查项目状态文件是否损坏

#### 8.2 调试技巧

1. **启用详细日志**：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **检查项目状态**：
```python
from project_manager import ProjectManager
manager = ProjectManager("my_project")
print(manager.get_current_status())
```

3. **验证配置文件**：
```python
import yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
print(config)
```

4. **检查自动化工作流状态**：
```python
from project_manager.auto_workflow import AutoWorkflow
auto_workflow = AutoWorkflow("my_project")
status = auto_workflow.get_workflow_status()
print(status)
```

### 9. 最佳实践

#### 9.1 开发流程
1. **优先使用自动化工作流**：减少手动干预，提高效率
2. 始终先检查项目状态
3. 严格按照阶段要求开发
4. 确保代码质量和规范性
5. 及时更新项目状态
6. 定期进行代码评审

#### 9.2 代码质量
1. 遵循PEP 8编码规范
2. 添加完整的类型注解
3. 包含详细的docstring
4. 实现完整的错误处理
5. 确保充分的测试覆盖

#### 9.3 项目管理
1. 保持状态文件的一致性
2. 定期备份项目数据
3. 记录开发日志和变更
4. 及时处理Critical问题
5. 遵循质量门禁要求

#### 9.4 自动化工作流使用
1. **选择合适的自动化模式**：
   - 标准自动化：适合一般项目
   - 智能自动化：适合有明确质量要求的项目
   - 持续改进：适合追求高质量的项目

2. **设置合理的参数**：
   - 目标分数：根据项目要求设置
   - 最大迭代次数：避免无限循环
   - 最大阶段数：控制项目范围

3. **监控工作流状态**：
   - 定期检查工作流进度
   - 关注Critical问题
   - 及时处理异常情况

### 10. 总结

通过以上配置和使用方法，Cursor AI将能够：

1. **严格按照项目管理模板**进行开发
2. **自动遵循代码质量要求**
3. **正确更新项目状态**
4. **提供准确的评审结果**
5. **保持开发流程的一致性**
6. **实现完全自动化的开发流程**

**强烈推荐使用自动化工作流**，这样可以：
- 最小化手动干预
- 提高开发效率
- 确保质量一致性
- 减少人为错误
- 实现真正的AI驱动开发

这样，你就可以充分利用Cursor AI的强大功能，同时确保开发过程符合你的项目管理标准，实现高效的自动化开发流程。
