import os
from dotenv import load_dotenv
from enum import Enum
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

load_dotenv()


class ModelProvider(Enum):
    DEEPSEEK = "deepseek"
    LOCAL = "local"  # 如需本地模型备用


class Settings:
    # ========== API Keys ==========
    WIND_API_KEY = os.getenv("WIND_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

    # ========== Model Configuration ==========
    MODEL_PROVIDER = ModelProvider.DEEPSEEK  # 核心切换点

    # DeepSeek模型参数（最新可用模型）
    EMBEDDING_MODEL = "deepseek-embedding"  # 官方API提供的embedding模型
    LLM_MODEL = "deepseek-chat"  # 官方API提供的对话模型
    LLM_TEMPERATURE = 0.3  # 控制生成随机性
    LLM_MAX_TOKENS = 4096  # 最大token限制

    # ========== Paths ==========
    DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
    VECTOR_DB_PATH = os.path.join(DATA_DIR, "vector_db/deepseek")  # 区分不同embedding模型

    # ========== RAG Parameters ==========
    RETRIEVE_TOP_K = 5  # 检索返回的文档数量
    SIMILARITY_THRESHOLD = 0.75  # 相似度阈值

    # ========== Experimental Features ==========
    USE_LOCAL_LLM = False  # 是否启用本地备用模型

    @classmethod
    def get_embedding_model(cls):
        """根据配置返回embedding模型实例"""
        if cls.MODEL_PROVIDER == ModelProvider.DEEPSEEK:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-zh-v1.5",  # 中文优化的小模型
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
        else:
            raise ValueError(f"Unsupported provider: {cls.MODEL_PROVIDER}")

    @classmethod
    def get_llm(cls):
        """根据配置返回LLM实例"""
        if cls.MODEL_PROVIDER == ModelProvider.DEEPSEEK:
            from langchain_community.llms import DeepSeek
            return DeepSeek(
                model=cls.LLM_MODEL,
                api_key=cls.DEEPSEEK_API_KEY,
                temperature=cls.LLM_TEMPERATURE,
                max_tokens=cls.LLM_MAX_TOKENS
            )
        else:
            raise ValueError(f"Unsupported provider: {cls.MODEL_PROVIDER}")


# 单例模式
settings = Settings()