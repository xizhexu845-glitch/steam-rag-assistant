import os
import json
import time
from tqdm import tqdm
from langchain_chroma import Chroma
from DataProcess.steam_json_process import json_to_docs
from DataProcess.zhipuai_embedding import ZhipuAIEmbeddings
from api_config.api import ZHIYUAI_API_KEY

# 设置参数常量
PERSIST_DIRECTORY = 'data_base/vector_db/chroma'
BATCH_SIZE = 64
UPDATE_JSON_PATH = 'data_base/steamapp_update.json'  # 你要删除的文件路径

def chroma_update(json_path):
    """
    使用智谱AI Embedding 对文档进行向量化并插入 Chroma 向量数据库
    :param json_path: 包含 Steam 游戏信息的 JSON 文件路径
    """

    # 设置 API Key 和清理 SSL 设置
    os.environ["ZHIPUAI_API_KEY"] = ZHIYUAI_API_KEY


    # 初始化 Embedding 模型和 Chroma 向量库
    embedding_model = ZhipuAIEmbeddings()
    vectordb = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embedding_model)

    # 加载 JSON 数据
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"❌ 无法加载 JSON 文件: {e}")
        return

    # 解析为文档格式
    docs = json_to_docs(json_data)


    if not docs:
        print("⚠️ 无有效文档，操作终止。")
        return

    # 分批嵌入并插入向量数据库
    print(f"🚀 开始向量化 {len(docs)} 条文档数据，写入 Chroma 向量库...")
    for i in tqdm(range(0, len(docs), BATCH_SIZE), desc="Embedding & Inserting"):
        batch = docs[i:i + BATCH_SIZE]
        ids = [doc['id'] for doc in batch]
        texts = [doc['content'] for doc in batch]
        embeddings = embedding_model.embed_documents(texts)

        vectordb._collection.upsert(
            ids=ids,
            documents=texts,      # ✅ 用 documents，不是 texts
            embeddings=embeddings
        )

    print(f"✅ 向量数据库更新完成，共处理 {len(docs)} 条文档。")

