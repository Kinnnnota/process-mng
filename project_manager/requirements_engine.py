"""
要件定义引擎
支持自然语言描述转换为具体项目配置
"""
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime


class RequirementsEngine:
    """要件定义引擎"""
    
    def __init__(self):
        """初始化要件定义引擎"""
        self.tech_stack_templates = self._load_tech_stack_templates()
        self.config_templates = self._load_config_templates()
    
    def parse_requirements(self, natural_language: str) -> Dict[str, Any]:
        """
        解析自然语言描述，生成项目要件配置
        
        Args:
            natural_language: 自然语言描述
            
        Returns:
            项目要件配置字典
        """
        # 解析技术栈
        tech_stack = self._parse_tech_stack(natural_language)
        
        # 解析项目类型
        project_type = self._parse_project_type(natural_language)
        
        # 解析部署要求
        deployment = self._parse_deployment(natural_language)
        
        # 解析数据库要求
        database = self._parse_database(natural_language)
        
        # 解析性能要求
        performance = self._parse_performance(natural_language)
        
        # 生成完整配置
        requirements = {
            'project_info': {
                'name': self._extract_project_name(natural_language),
                'description': natural_language,
                'created_at': datetime.now().isoformat(),
                'version': '1.0.0'
            },
            'tech_stack': tech_stack,
            'project_type': project_type,
            'database': database,
            'deployment': deployment,
            'performance': performance,
            'development_config': self._generate_dev_config(tech_stack, project_type),
            'deployment_config': self._generate_deployment_config(deployment),
            'database_config': self._generate_database_config(database)
        }
        
        return requirements
    
    def generate_config_files(self, requirements: Dict[str, Any], project_name: str) -> Dict[str, str]:
        """
        根据要件配置生成具体的配置文件
        
        Args:
            requirements: 要件配置
            project_name: 项目名称
            
        Returns:
            配置文件路径字典
        """
        project_dir = Path(f"project_manager/{project_name}")
        config_dir = project_dir / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_files = {}
        
        # 生成技术栈配置文件
        tech_stack_config = self._generate_tech_stack_config(requirements['tech_stack'])
        tech_stack_file = config_dir / "tech_stack.json"
        with open(tech_stack_file, 'w', encoding='utf-8') as f:
            json.dump(tech_stack_config, f, ensure_ascii=False, indent=2)
        config_files['tech_stack'] = str(tech_stack_file)
        
        # 生成数据库配置文件
        db_config = self._generate_database_config(requirements['database'])
        db_file = config_dir / "database.json"
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(db_config, f, ensure_ascii=False, indent=2)
        config_files['database'] = str(db_file)
        
        # 生成部署配置文件
        deploy_config = self._generate_deployment_config(requirements['deployment'])
        deploy_file = config_dir / "deployment.json"
        with open(deploy_file, 'w', encoding='utf-8') as f:
            json.dump(deploy_config, f, ensure_ascii=False, indent=2)
        config_files['deployment'] = str(deploy_file)
        
        # 生成开发环境配置文件
        dev_config = self._generate_dev_config(requirements['tech_stack'], requirements['project_type'])
        dev_file = config_dir / "development.json"
        with open(dev_file, 'w', encoding='utf-8') as f:
            json.dump(dev_config, f, ensure_ascii=False, indent=2)
        config_files['development'] = str(dev_file)
        
        # 生成项目要件文档
        requirements_doc = self._generate_requirements_doc(requirements)
        doc_file = config_dir / "requirements.md"
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(requirements_doc)
        config_files['requirements_doc'] = str(doc_file)
        
        return config_files
    
    def _parse_tech_stack(self, text: str) -> Dict[str, Any]:
        """解析技术栈"""
        tech_stack = {
            'language': 'Python',  # 默认
            'framework': None,
            'frontend': None,
            'backend': None,
            'database': None,
            'cache': None,
            'message_queue': None,
            'monitoring': None,
            'testing': None,
            'deployment': None
        }
        
        text_lower = text.lower()
        
        # 解析编程语言
        if 'python' in text_lower:
            tech_stack['language'] = 'Python'
        elif 'javascript' in text_lower or 'js' in text_lower:
            tech_stack['language'] = 'JavaScript'
        elif 'java' in text_lower:
            tech_stack['language'] = 'Java'
        elif 'c#' in text_lower or 'csharp' in text_lower:
            tech_stack['language'] = 'C#'
        elif 'go' in text_lower:
            tech_stack['language'] = 'Go'
        elif 'rust' in text_lower:
            tech_stack['language'] = 'Rust'
        
        # 解析框架
        if 'django' in text_lower:
            tech_stack['framework'] = 'Django'
        elif 'flask' in text_lower:
            tech_stack['framework'] = 'Flask'
        elif 'fastapi' in text_lower:
            tech_stack['framework'] = 'FastAPI'
        elif 'react' in text_lower:
            tech_stack['frontend'] = 'React'
        elif 'vue' in text_lower:
            tech_stack['frontend'] = 'Vue.js'
        elif 'angular' in text_lower:
            tech_stack['frontend'] = 'Angular'
        elif 'spring' in text_lower:
            tech_stack['framework'] = 'Spring Boot'
        elif 'express' in text_lower:
            tech_stack['framework'] = 'Express.js'
        
        # 解析数据库
        if 'mysql' in text_lower:
            tech_stack['database'] = 'MySQL'
        elif 'postgresql' in text_lower or 'postgres' in text_lower:
            tech_stack['database'] = 'PostgreSQL'
        elif 'mongodb' in text_lower:
            tech_stack['database'] = 'MongoDB'
        elif 'redis' in text_lower:
            tech_stack['cache'] = 'Redis'
        elif 'sqlite' in text_lower:
            tech_stack['database'] = 'SQLite'
        
        # 解析部署平台
        if 'docker' in text_lower:
            tech_stack['deployment'] = 'Docker'
        elif 'kubernetes' in text_lower or 'k8s' in text_lower:
            tech_stack['deployment'] = 'Kubernetes'
        elif 'aws' in text_lower:
            tech_stack['deployment'] = 'AWS'
        elif 'azure' in text_lower:
            tech_stack['deployment'] = 'Azure'
        elif 'gcp' in text_lower or 'google cloud' in text_lower:
            tech_stack['deployment'] = 'Google Cloud'
        elif 'heroku' in text_lower:
            tech_stack['deployment'] = 'Heroku'
        
        return tech_stack
    
    def _parse_project_type(self, text: str) -> str:
        """解析项目类型"""
        text_lower = text.lower()
        
        if 'web' in text_lower and 'app' in text_lower:
            return 'web_application'
        elif 'api' in text_lower or 'rest' in text_lower:
            return 'api_service'
        elif 'mobile' in text_lower or 'app' in text_lower:
            return 'mobile_app'
        elif 'desktop' in text_lower:
            return 'desktop_app'
        elif 'cli' in text_lower or 'command' in text_lower:
            return 'cli_tool'
        elif 'library' in text_lower or 'package' in text_lower:
            return 'library'
        else:
            return 'web_application'  # 默认
    
    def _parse_database(self, text: str) -> Dict[str, Any]:
        """解析数据库要求"""
        text_lower = text.lower()
        
        database = {
            'type': 'SQLite',  # 默认
            'host': 'localhost',
            'port': 5432,
            'name': 'app_db',
            'user': 'app_user',
            'password': '',
            'connection_pool': True,
            'migrations': True
        }
        
        if 'mysql' in text_lower:
            database['type'] = 'MySQL'
            database['port'] = 3306
        elif 'postgresql' in text_lower or 'postgres' in text_lower:
            database['type'] = 'PostgreSQL'
            database['port'] = 5432
        elif 'mongodb' in text_lower:
            database['type'] = 'MongoDB'
            database['port'] = 27017
        elif 'redis' in text_lower:
            database['type'] = 'Redis'
            database['port'] = 6379
        
        return database
    
    def _parse_deployment(self, text: str) -> Dict[str, Any]:
        """解析部署要求"""
        text_lower = text.lower()
        
        deployment = {
            'platform': 'local',  # 默认本地
            'containerization': False,
            'orchestration': False,
            'auto_scaling': False,
            'load_balancer': False,
            'ssl': False,
            'domain': '',
            'environment': 'development'
        }
        
        if 'docker' in text_lower:
            deployment['containerization'] = True
        if 'kubernetes' in text_lower or 'k8s' in text_lower:
            deployment['orchestration'] = True
        if 'aws' in text_lower:
            deployment['platform'] = 'AWS'
            deployment['auto_scaling'] = True
        if 'azure' in text_lower:
            deployment['platform'] = 'Azure'
        if 'gcp' in text_lower or 'google cloud' in text_lower:
            deployment['platform'] = 'Google Cloud'
        if 'production' in text_lower:
            deployment['environment'] = 'production'
            deployment['ssl'] = True
        
        return deployment
    
    def _parse_performance(self, text: str) -> Dict[str, Any]:
        """解析性能要求"""
        text_lower = text.lower()
        
        performance = {
            'response_time': 'normal',  # normal, fast, ultra_fast
            'concurrent_users': 100,
            'data_volume': 'small',  # small, medium, large
            'availability': 99.9,
            'caching': False,
            'cdn': False
        }
        
        if 'high performance' in text_lower or 'fast' in text_lower:
            performance['response_time'] = 'fast'
        if 'ultra fast' in text_lower or 'real-time' in text_lower:
            performance['response_time'] = 'ultra_fast'
        if 'high concurrency' in text_lower or 'many users' in text_lower:
            performance['concurrent_users'] = 1000
        if 'large scale' in text_lower or 'big data' in text_lower:
            performance['data_volume'] = 'large'
        if 'cache' in text_lower or 'caching' in text_lower:
            performance['caching'] = True
        if 'cdn' in text_lower:
            performance['cdn'] = True
        
        return performance
    
    def _extract_project_name(self, text: str) -> str:
        """提取项目名称"""
        # 简单的项目名称提取逻辑
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in ['project', 'system', 'app', 'application', 'service']:
                if i > 0:
                    return words[i-1].capitalize()
        return 'MyProject'
    
    def _generate_tech_stack_config(self, tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        """生成技术栈配置"""
        config = {
            'language': {
                'name': tech_stack['language'],
                'version': self._get_default_version(tech_stack['language']),
                'package_manager': self._get_package_manager(tech_stack['language'])
            },
            'framework': tech_stack['framework'],
            'frontend': tech_stack['frontend'],
            'backend': tech_stack['backend'],
            'database': tech_stack['database'],
            'cache': tech_stack['cache'],
            'message_queue': tech_stack['message_queue'],
            'monitoring': tech_stack['monitoring'],
            'testing': tech_stack['testing'],
            'deployment': tech_stack['deployment']
        }
        
        return config
    
    def _generate_database_config(self, database: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据库配置"""
        return {
            'type': database['type'],
            'connection': {
                'host': database['host'],
                'port': database['port'],
                'database': database['name'],
                'username': database['user'],
                'password': database['password']
            },
            'pool': database['connection_pool'],
            'migrations': database['migrations'],
            'backup': True,
            'monitoring': True
        }
    
    def _generate_deployment_config(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """生成部署配置"""
        return {
            'platform': deployment['platform'],
            'containerization': deployment['containerization'],
            'orchestration': deployment['orchestration'],
            'auto_scaling': deployment['auto_scaling'],
            'load_balancer': deployment['load_balancer'],
            'ssl': deployment['ssl'],
            'domain': deployment['domain'],
            'environment': deployment['environment']
        }
    
    def _generate_dev_config(self, tech_stack: Dict[str, Any], project_type: str) -> Dict[str, Any]:
        """生成开发环境配置"""
        return {
            'ide': 'VS Code',
            'version_control': 'Git',
            'code_quality': ['flake8', 'black', 'mypy'],
            'testing': ['pytest', 'coverage'],
            'documentation': 'Sphinx',
            'ci_cd': 'GitHub Actions'
        }
    
    def _generate_requirements_doc(self, requirements: Dict[str, Any]) -> str:
        """生成要件文档"""
        doc = f"""# {requirements['project_info']['name']} 项目要件定义

## 项目概述
{requirements['project_info']['description']}

## 技术栈
- **编程语言**: {requirements['tech_stack']['language']}
- **框架**: {requirements['tech_stack']['framework'] or '无'}
- **前端**: {requirements['tech_stack']['frontend'] or '无'}
- **数据库**: {requirements['tech_stack']['database'] or '无'}
- **缓存**: {requirements['tech_stack']['cache'] or '无'}
- **部署**: {requirements['tech_stack']['deployment'] or '无'}

## 项目类型
{requirements['project_type']}

## 数据库配置
- **类型**: {requirements['database']['type']}
- **主机**: {requirements['database']['host']}
- **端口**: {requirements['database']['port']}
- **数据库名**: {requirements['database']['name']}

## 部署配置
- **平台**: {requirements['deployment']['platform']}
- **容器化**: {'是' if requirements['deployment']['containerization'] else '否'}
- **编排**: {'是' if requirements['deployment']['orchestration'] else '否'}
- **自动扩缩容**: {'是' if requirements['deployment']['auto_scaling'] else '否'}

## 性能要求
- **响应时间**: {requirements['performance']['response_time']}
- **并发用户数**: {requirements['performance']['concurrent_users']}
- **数据量**: {requirements['performance']['data_volume']}
- **可用性**: {requirements['performance']['availability']}%

## 开发环境
- **IDE**: {requirements['development_config']['ide']}
- **版本控制**: {requirements['development_config']['version_control']}
- **代码质量工具**: {', '.join(requirements['development_config']['code_quality'])}
- **测试工具**: {', '.join(requirements['development_config']['testing'])}

---
生成时间: {requirements['project_info']['created_at']}
版本: {requirements['project_info']['version']}
"""
        return doc
    
    def _get_default_version(self, language: str) -> str:
        """获取默认版本"""
        versions = {
            'Python': '3.11',
            'JavaScript': '18.x',
            'Java': '17',
            'C#': '11.0',
            'Go': '1.21',
            'Rust': '1.70'
        }
        return versions.get(language, 'latest')
    
    def _get_package_manager(self, language: str) -> str:
        """获取包管理器"""
        managers = {
            'Python': 'pip',
            'JavaScript': 'npm',
            'Java': 'Maven',
            'C#': 'NuGet',
            'Go': 'go mod',
            'Rust': 'Cargo'
        }
        return managers.get(language, 'default')
    
    def _load_tech_stack_templates(self) -> Dict[str, Any]:
        """加载技术栈模板"""
        return {
            'python_web': {
                'language': 'Python',
                'framework': 'Django',
                'database': 'PostgreSQL',
                'cache': 'Redis'
            },
            'python_api': {
                'language': 'Python',
                'framework': 'FastAPI',
                'database': 'PostgreSQL',
                'cache': 'Redis'
            },
            'javascript_web': {
                'language': 'JavaScript',
                'framework': 'Express.js',
                'frontend': 'React',
                'database': 'MongoDB'
            }
        }
    
    def _load_config_templates(self) -> Dict[str, Any]:
        """加载配置模板"""
        return {
            'development': {
                'environment': 'development',
                'debug': True,
                'logging': 'DEBUG'
            },
            'production': {
                'environment': 'production',
                'debug': False,
                'logging': 'INFO'
            }
        }
