更新：支持语义检索（sentence-transformers + faiss）与 LLM 生成（OpenAI 或本地 HuggingFace 模型）。

使用方法：
- 若要使用 OpenAI，请在环境变量中设置 OPENAI_API_KEY。
- 若使用本地模型，请在环境变量 LOCAL_MODEL_NAME 指定模型（例如：'gpt2' 或 HuggingFace 上的模型标识）。
- 安装依赖并重建索引：
  pip install -r requirements.txt
  python scripts/build_index.py

注意：本地模型可能需要 GPU 和显存，使用大型模型请在有相应硬件的机器上运行。
