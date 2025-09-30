from langchain_community.vectorstores import Chroma
from config.settings import settings
from typing import List, Dict, Optional
import logging
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    def __init__(self):
        """初始化DeepSeek向量检索器"""
        try:
            self.vectorstore = Chroma(
                persist_directory=settings.VECTOR_DB_PATH,
                embedding_function=settings.get_embedding_model()
            )
            logger.info("DeepSeek向量检索器初始化成功")
        except Exception as e:
            logger.error(f"向量数据库加载失败: {e}")
            raise

    def query(
            self,
            question: str,
            k: int = settings.RETRIEVE_TOP_K,
            filter_criteria: Optional[Dict] = None
    ) -> List[Dict]:
        """
        检索与问题最相关的文档片段
        :param question: 查询问题
        :param k: 返回结果数量 (默认取settings.RETRIEVE_TOP_K)
        :param filter_criteria: 元数据过滤条件 (如: {"source": "wind"})
        :return: [{"content": str, "metadata": dict, "score": float}]
        """
        try:
            # DeepSeek的相似度检索
            docs_and_scores = self.vectorstore.similarity_search_with_score(
                question,
                k=k,
                filter=filter_criteria
            )

            # 标准化输出格式
            results = []
            for doc, score in docs_and_scores:
                if score < settings.SIMILARITY_THRESHOLD:
                    logger.debug(f"过滤低分文档: score={score:.2f}")
                    continue

                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })

            logger.info(f"检索完成: query='{question}', results={len(results)}")
            return results

        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []

    def add_documents(self, documents: List[Document]) -> bool:
        """向知识库添加新文档"""
        try:
            self.vectorstore.add_documents(documents)
            logger.info(f"成功添加 {len(documents)} 个文档")
            return True
        except Exception as e:
            logger.error(f"文档添加失败: {e}")
            return False

    @property
    def document_count(self) -> int:
        """获取知识库中文档数量"""
        try:
            return self.vectorstore._collection.count()  # ChromaDB内部API
        except Exception as e:
            logger.warning(f"文档计数失败: {e}")
            return 0


# 单例模式
retriever = KnowledgeRetriever()