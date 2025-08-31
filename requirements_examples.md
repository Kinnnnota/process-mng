# 项目要件定义示例

## 概述
本文档展示如何使用自然语言描述项目要件，系统会自动解析并生成具体的配置文件。

## 使用方法

### 基本语法
```bash
python main.py define --project "项目名" --requirements "自然语言描述"
```

### 示例1：Python Web应用
```bash
python main.py define --project "电商系统" --requirements "使用Python和Django开发一个电商网站，使用PostgreSQL数据库，Redis缓存，部署到AWS，支持高并发"
```

**解析结果：**
- 编程语言：Python
- 框架：Django
- 数据库：PostgreSQL
- 缓存：Redis
- 部署平台：AWS
- 性能要求：高并发

### 示例2：JavaScript API服务
```bash
python main.py define --project "用户API" --requirements "使用JavaScript和Express.js开发REST API，使用MongoDB数据库，部署到Docker容器，支持实时通信"
```

**解析结果：**
- 编程语言：JavaScript
- 框架：Express.js
- 数据库：MongoDB
- 部署：Docker
- 项目类型：API服务

### 示例3：移动应用后端
```bash
python main.py define --project "移动后端" --requirements "使用Python和FastAPI开发移动应用后端，使用MySQL数据库，部署到Google Cloud，需要高性能和实时推送"
```

**解析结果：**
- 编程语言：Python
- 框架：FastAPI
- 数据库：MySQL
- 部署平台：Google Cloud
- 性能要求：高性能

### 示例4：桌面应用
```bash
python main.py define --project "桌面工具" --requirements "使用Python开发桌面应用程序，使用SQLite数据库，支持离线运行，需要跨平台"
```

**解析结果：**
- 编程语言：Python
- 数据库：SQLite
- 项目类型：桌面应用
- 部署：本地

### 示例5：CLI工具
```bash
python main.py define --project "CLI工具" --requirements "使用Python开发命令行工具，不需要数据库，支持多种操作系统，需要打包成可执行文件"
```

**解析结果：**
- 编程语言：Python
- 项目类型：CLI工具
- 数据库：无
- 部署：本地

## 支持的技术栈

### 编程语言
- Python
- JavaScript
- Java
- C#
- Go
- Rust

### 框架
- Django (Python)
- Flask (Python)
- FastAPI (Python)
- React (JavaScript)
- Vue.js (JavaScript)
- Angular (JavaScript)
- Spring Boot (Java)
- Express.js (JavaScript)

### 数据库
- MySQL
- PostgreSQL
- MongoDB
- SQLite
- Redis (缓存)

### 部署平台
- Docker
- Kubernetes
- AWS
- Azure
- Google Cloud
- Heroku

## 性能关键词

### 响应时间
- "fast" / "high performance" → 快速响应
- "ultra fast" / "real-time" → 超快速响应
- "normal" → 普通响应（默认）

### 并发用户
- "high concurrency" / "many users" → 1000并发用户
- "normal" → 100并发用户（默认）

### 数据量
- "large scale" / "big data" → 大数据量
- "medium" → 中等数据量
- "small" → 小数据量（默认）

### 缓存
- "cache" / "caching" → 启用缓存
- "no cache" → 不启用缓存

## 项目类型识别

### Web应用
关键词：web, website, 网站, 网页
```
"开发一个Web应用"
"创建一个网站"
"网页应用"
```

### API服务
关键词：api, rest, service, 接口
```
"开发REST API"
"创建API服务"
"后端接口"
```

### 移动应用
关键词：mobile, app, 移动, 手机
```
"移动应用"
"手机APP"
"移动端"
```

### 桌面应用
关键词：desktop, 桌面, 客户端
```
"桌面应用"
"客户端程序"
"桌面软件"
```

### CLI工具
关键词：cli, command, 命令行, 工具
```
"命令行工具"
"CLI应用"
"终端工具"
```

## 配置文件生成

系统会根据要件定义自动生成以下配置文件：

### 1. tech_stack.yaml
```yaml
language:
  name: Python
  version: 3.11
  package_manager: pip
framework: Django
database: PostgreSQL
cache: Redis
deployment: AWS
```

### 2. database.yaml
```yaml
type: PostgreSQL
connection:
  host: localhost
  port: 5432
  database: app_db
  username: app_user
  password: ""
pool: true
migrations: true
backup: true
monitoring: true
```

### 3. deployment.yaml
```yaml
platform: AWS
containerization: false
orchestration: false
auto_scaling: true
load_balancer: false
ssl: false
domain: ""
environment: development
```

### 4. development.yaml
```yaml
ide: VS Code
version_control: Git
code_quality:
  - flake8
  - black
  - mypy
testing:
  - pytest
  - coverage
documentation: Sphinx
ci_cd: GitHub Actions
```

### 5. requirements.md
生成完整的项目要件文档，包含所有配置信息。

## 查看要件配置

```bash
python main.py requirements --project "项目名"
```

输出示例：
```
📋 项目要件配置：电商系统
🔧 技术栈：Python
🏗️  框架：Django
🗄️  数据库：PostgreSQL
🚀 部署平台：AWS
📊 项目类型：web_application
```

## 更新要件配置

```bash
python main.py define --project "项目名" --requirements "新的需求描述"
```

系统会：
1. 解析新的需求描述
2. 更新所有配置文件
3. 生成新的要件文档
4. 更新项目状态

## 最佳实践

### 1. 描述要清晰具体
✅ 好的描述：
```
"使用Python和Django开发电商网站，使用PostgreSQL数据库，Redis缓存，部署到AWS，支持高并发用户"
```

❌ 模糊的描述：
```
"开发一个网站"
```

### 2. 包含关键技术信息
- 编程语言
- 框架选择
- 数据库类型
- 部署平台
- 性能要求

### 3. 考虑扩展性
- 是否需要缓存
- 是否需要消息队列
- 是否需要监控
- 是否需要负载均衡

### 4. 性能要求明确
- 并发用户数
- 响应时间要求
- 数据量大小
- 可用性要求

## 注意事项

1. **自然语言解析**：系统使用关键词匹配，建议使用标准的技术术语
2. **默认配置**：未明确指定的配置会使用默认值
3. **配置文件**：生成的配置文件可以手动修改
4. **版本管理**：要件配置会保存在项目状态中
5. **向后兼容**：更新要件不会影响已有的开发成果

## 故障排除

### 问题1：解析结果不符合预期
- 检查是否使用了支持的关键词
- 尝试使用更具体的描述
- 查看生成的配置文件进行确认

### 问题2：配置文件生成失败
- 检查项目目录权限
- 确保项目已正确初始化
- 查看错误日志

### 问题3：要件配置丢失
- 检查项目状态文件
- 重新定义要件
- 备份重要配置

---

通过要件定义系统，你可以用自然语言快速定义项目技术栈和配置，系统会自动生成相应的配置文件，大大简化项目初始化过程！
