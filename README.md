一个兴趣项目，探索让 AI 自己审查自己生成代码的可行性。

核心想法是：既然 AI 能写代码，那能不能让它像人类 Reviewer 一样，看不到历史记录，纯粹基于当前代码给出评审意见

看看能不能实现真正的"黑箱评审"。



去 [Anthropic Console](https://console.anthropic.com/) 弄个 API 密钥

然后创建 `.env` 文件：
```bash
cp .env.example .env
# 编辑 .env，把 API key 填进去
ANTHROPIC_API_KEY=your_api_key_here
```

```bash
# 初始化项目
python main.py init --project "my_project"

# 全自动运行
python main.py auto --project "my_project"

# 智能模式（冲 85 分）
python main.py smart --project "my_project" --score 85

# 持续改进模式
python main.py improve --project "my_project" --phases 5
```
