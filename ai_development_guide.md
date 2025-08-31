# AI开发指导手册

## 概述
本文件指导Cursor AI如何严格按照项目管理模板进行开发。系统支持完全自动化的开发流程，最小化手动干预。

## 开发流程

### 1. 项目初始化
当用户要求创建新项目时：
1. 读取 `config.yaml` 配置文件
2. 创建项目目录结构
3. 初始化项目状态文件
4. 设置当前阶段为 `BASIC_DESIGN`

### 2. 自动化工作流（推荐方式）

#### 2.1 完全自动化开发
**触发条件**：用户要求运行自动化工作流

**AI行为**：
1. 创建 `AutoWorkflow` 实例
2. 自动执行以下循环：
   - 切换到开发模式生成内容
   - 切换到评审模式评估内容
   - 根据评分决定是否进入下一阶段
   - 自动处理迭代和改进
3. 生成完整的项目报告

**代码示例**：
```python
from project_manager.auto_workflow import AutoWorkflow

def run_automated_development(project_name: str):
    """运行完全自动化开发流程"""
    auto_workflow = AutoWorkflow(project_name)
    result = auto_workflow.run_auto_workflow()
    
    print(f"🤖 自动化工作流完成：{result['status']}")
    print(f"📊 完成阶段数：{len(result['phases_completed'])}")
    print(f"🔄 总迭代次数：{result['total_iterations']}")
    
    return result
```

#### 2.2 智能工作流
**触发条件**：用户要求达到特定质量目标

**AI行为**：
1. 设置目标分数
2. 自动优化直到达到目标
3. 达到目标后自动进入下一阶段

**代码示例**：
```python
def run_smart_workflow(project_name: str, target_score: float = 85.0):
    """运行智能工作流"""
    auto_workflow = AutoWorkflow(project_name)
    result = auto_workflow.run_smart_workflow(target_score)
    
    print(f"🧠 智能工作流完成：{result['status']}")
    print(f"🎯 目标分数：{target_score}")
    print(f"⭐ 最终评分：{result['final_score']}")
    
    return result
```

### 3. 开发模式（Developer Mode）

#### 3.1 基本设计阶段
**触发条件**：当前阶段为 `BASIC_DESIGN`

**AI行为**：
1. 读取 `project_manager/prompts/developer_mode.md` 中的设计阶段提示词
2. 生成包含以下内容的设计文档：
   - 项目概述
   - 业务流程图（mermaid格式）
   - 系统架构图
   - ER图和表结构
   - API接口清单
3. 保存到 `project_manager/{project_name}/phase_outputs/basic_design/basic_design_v{iteration}.md`
4. 更新项目状态为 `READY_FOR_REVIEW`

**代码示例**：
```python
def _generate_basic_design_document(self, iteration: int) -> str:
    """生成基本设计文档"""
    # 读取提示词模板
    prompt_template = self._load_prompt("developer_mode.md")
    
    # 生成设计内容
    content = f"""# {self.project_name} 基本设计文档 (第{iteration + 1}次迭代)
    
    ## 1. 项目概述
    [根据提示词模板生成项目概述]
    
    ## 2. 业务流程图
    ```mermaid
    [生成业务流程图]
    ```
    
    ## 3. 系统架构图
    [生成系统架构图]
    
    ## 4. ER图和表结构
    [生成数据库设计]
    
    ## 5. API接口清单
    [生成API接口定义]
    """
    
    return content
```

#### 3.2 详细设计阶段
**触发条件**：当前阶段为 `DETAIL_DESIGN`

**AI行为**：
1. 读取详细设计阶段的提示词
2. 生成包含以下内容的设计文档：
   - 类图设计
   - 算法伪代码
   - 数据结构定义
   - 时序图
3. 保存到 `project_manager/{project_name}/phase_outputs/detail_design/detail_design_v{iteration}.md`

#### 3.3 开发实现阶段
**触发条件**：当前阶段为 `DEVELOPMENT`

**AI行为**：
1. 读取开发阶段的提示词
2. 生成符合设计文档的代码实现
3. 确保代码质量：
   - 遵循PEP 8规范
   - 包含完整的错误处理
   - 添加详细的注释
   - 考虑性能优化
4. 保存到 `project_manager/{project_name}/phase_outputs/development/implementation_v{iteration}.py`

#### 3.4 单元测试阶段
**触发条件**：当前阶段为 `UNIT_TEST`

**AI行为**：
1. 读取测试阶段的提示词
2. 生成完整的测试用例：
   - 单元测试
   - 边界测试
   - 异常测试
3. 确保测试覆盖率达到80%以上
4. 保存到 `project_manager/{project_name}/phase_outputs/unit_test/unit_test_v{iteration}.py`

#### 3.5 集成测试阶段
**触发条件**：当前阶段为 `INTEGRATION_TEST`

**AI行为**：
1. 读取集成测试阶段的提示词
2. 生成集成测试用例：
   - 端到端测试
   - 性能测试
   - 稳定性测试
3. 保存到 `project_manager/{project_name}/phase_outputs/integration_test/integration_test_v{iteration}.py`

### 4. 评审模式（Reviewer Mode）

#### 4.1 评审流程
**触发条件**：当前模式为 `REVIEWER`

**AI行为**：
1. 读取当前阶段的输出文件
2. 按照评审标准进行评估
3. 生成评审结果：
   - 总分（25分制）
   - 问题分级（Critical/Major/Minor）
   - 改进建议
   - 检查项得分
4. 更新项目状态和评审历史

**代码示例**：
```python
def review_phase(self) -> Dict[str, Any]:
    """评审当前阶段成果"""
    if self.state.current_mode != Mode.REVIEWER:
        raise ValueError("当前不是评审模式")
    
    # 读取当前阶段的输出文件
    content = self._read_phase_output()
    
    # 执行评审
    review_result = self.review_engine.evaluate(
        self.state.current_phase, 
        content
    )
    
    # 更新项目状态
    self.state.phase_scores.append(review_result['score'])
    self._save_state()
    
    return review_result
```

### 5. 阶段转换逻辑

#### 5.1 自动转换条件
**触发条件**：评审分数达到通过标准

**AI行为**：
1. 检查当前阶段评分
2. 检查是否达到通过分数
3. 检查是否超过最大迭代次数
4. 自动进入下一阶段或继续迭代

#### 5.2 强制转换
**触发条件**：达到最大迭代次数或用户要求

**AI行为**：
1. 强制进入下一阶段
2. 重置迭代计数器
3. 记录强制转换原因

#### 5.3 智能回退
**触发条件**：检测到Critical问题

**AI行为**：
1. 分析Critical问题
2. 确定回退目标阶段
3. 执行回退操作
4. 记录回退原因

### 6. 质量保证

#### 6.1 代码质量要求
- **功能完整性**：35%
- **代码规范**：25%
- **异常处理**：20%
- **性能优化**：20%

#### 6.2 测试质量要求
- **测试覆盖率**：35%
- **边界测试**：30%
- **异常测试**：35%

#### 6.3 设计质量要求
- **业务完整性**：30%
- **架构合理性**：25%
- **数据库设计**：25%
- **接口定义**：20%

### 7. 错误处理

#### 7.1 异常处理策略
1. **文件操作异常**：创建默认文件或使用备份
2. **状态转换异常**：回退到安全状态
3. **评审异常**：使用默认评分
4. **配置异常**：使用默认配置

#### 7.2 错误恢复机制
1. **自动重试**：临时错误自动重试
2. **状态回滚**：错误时回滚到安全状态
3. **日志记录**：详细记录错误信息
4. **用户通知**：友好的错误提示

### 8. 性能优化

#### 8.1 文件操作优化
1. **缓存机制**：缓存频繁读取的文件
2. **批量操作**：减少文件I/O次数
3. **异步处理**：非关键操作异步执行

#### 8.2 内存管理
1. **及时释放**：及时释放不需要的资源
2. **内存监控**：监控内存使用情况
3. **垃圾回收**：主动触发垃圾回收

### 9. 最佳实践

#### 9.1 开发模式最佳实践
1. **严格按照提示词模板**生成内容
2. **确保覆盖所有检查项**要求
3. **关注代码规范和最佳实践**
4. **添加充分的注释和文档**

#### 9.2 评审模式最佳实践
1. **客观公正地进行评估**
2. **重点关注Critical和Major级别问题**
3. **每次只关注一个最重要的改进点**
4. **提供具体、可操作的改进建议**

#### 9.3 自动化工作流最佳实践
1. **优先使用自动化工作流**减少手动干预
2. **选择合适的自动化模式**根据项目需求
3. **设置合理的参数**避免无限循环
4. **监控工作流状态**及时处理异常

### 10. 总结

通过以上指导，Cursor AI将能够：

1. **严格按照项目管理模板**进行开发
2. **自动遵循代码质量要求**
3. **正确更新项目状态**
4. **提供准确的评审结果**
5. **保持开发流程的一致性**
6. **实现完全自动化的开发流程**

**强烈推荐使用自动化工作流**，这样可以最大化减少手动干预，提高开发效率，确保质量一致性。
