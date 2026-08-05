# 个性化膳食规划 Agent - 项目骨架

说明
- 这是一个轻量可运行的个性化膳食规划系统原型（FastAPI）。
- 功能：菜谱加载 / 检索、硬约束过滤、简单膳食规划、多轮对话 harness、自动评分脚本。
- 适合在本地或评测服务器进一步替换真实菜谱库与接入大型模型扩展。

快速开始
1. 克隆或把本项目文件放到本地目录。
2. 创建虚拟环境并安装依赖：
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
3. 准备数据：
   - 把你的完整菜谱 JSON 放到 data/recipes.json（示例格式见 data/sample_recipes.json）
   - 可选：把用户健康档案放到 data/users.json
4. 构建索引（首次或数据变更后）：
   python scripts/build_index.py
5. 启动服务：
   uvicorn app.main:app --reload --port 8000
6. 运行自动化测试/评分：
   python tests/harness.py data/对话用例.json

主要接口
- POST /plan
  请求：UserProfile + constraints（time_limit, prefer_main, avoid_ingredients 等）
  返回：推荐菜谱清单、每道菜来源 ID、营养估算、替代建议
- POST /dialogue
  请求：session_id, user_utterance（用于多轮交互，内部维护上下文）
  返回：Agent 回复（推荐或澄清问题）

注意
- 当前检索使用 TF-IDF，生产建议用语义向量（sentence-transformers）替换以提升召回。
- 若要集成 LLM 生成详细解释或多候选序列，请在 planner.py 内调用模型并把 prompt 模板传入。

欢迎告诉我是否要：
- 把此项目推到 GitHub 仓库（请提供 owner/repo）。
- 把检索升级为 sentence-transformers + FAISS。
- 集成 OpenAI 或本地 LLM（我会帮你加密钥管理与 prompt 设计）。
