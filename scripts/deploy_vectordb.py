#!/usr/bin/env python3
"""
知识库初始化脚本：
1. 加载原始文档（PDF/HTML/CSV）
2. 文本分割与向量化
3. 持久化到ChromaDB
"""
from pathlib import Path
from knowledge_base.loader import load_documents
from knowledge_base.splitter import get_text_splitter
from config.settings import Settings
from utils.logger import setup_logger
import argparse

logger = setup_logger("deploy_vectordb")

def init_vector_db(data_dir: str, vector_db_path: str):
    """初始化向量数据库"""
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings

    if not Path(data_dir).exists():
        raise FileNotFoundError(f"数据目录不存在: {data_dir}")

    # 加载并处理文档
    documents = []
    for file in Path(data_dir).glob("*.*"):
        try:
            docs = load_documents(str(file))
            splitter = get_text_splitter(file.suffix[1:])
            splits = splitter.split_documents(docs)
            documents.extend(splits)
            logger.info(f"已处理: {file.name} → {len(splits)} chunks")
        except Exception as e:
            logger.error(f"处理失败 {file}: {e}")

    # 持久化向量存储
    if documents:
        Chroma.from_documents(
            documents=documents,
            embedding=OpenAIEmbeddings(model=Settings.EMBEDDING_MODEL),
            persist_directory=vector_db_path
        )
        logger.info(f"向量数据库已初始化: {vector_db_path}")
    else:
        logger.warning("未找到有效文档，跳过初始化")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default=f"{Settings.DATA_DIR}/raw", help="原始文档路径")
    parser.add_argument("--vector_db", default=Settings.VECTOR_DB_PATH, help="向量数据库存储路径")
    args = parser.parse_args()

    init_vector_db(args.data_dir, args.vector_db)