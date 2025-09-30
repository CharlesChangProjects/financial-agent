from langchain_core.language_models import BaseLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.pydantic_v1 import Field
from langchain_core.outputs import LLMResult
from config.settings import settings
from typing import Any, Dict, List, Optional, Union, Iterator
import requests
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class DeepSeekLLM(BaseLLM):
    """
    DeepSeek LLM 完整实现（兼容 LangChain BaseLLM 接口）
    必须实现 _generate 和 _llm_type 方法
    """
    api_key: str = Field(exclude=True, description="DeepSeek API 密钥")
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2048
    api_base: str = "https://api.deepseek.com/v1"
    request_timeout: int = 30

    @property
    def _llm_type(self) -> str:
        """标识 LLM 类型"""
        return "deepseek"

    def _generate(
            self,
            prompts: List[str],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> LLMResult:
        """
        核心方法：处理批量输入并返回 LLMResult
        （LangChain 框架会调用此方法）
        """
        responses = []
        for prompt in prompts:
            response = self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
            responses.append(response)
        return LLMResult(generations=[[{"text": r} for r in responses]])

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        """调用 DeepSeek API 生成单个响应"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs
        }
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.request_timeout
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API 请求失败: {str(e)}")
            raise
        except KeyError:
            logger.error("DeepSeek API 响应格式异常")
            raise ValueError("无效的 API 响应")


class BaseAgent:
    """
    Agent 基类（DeepSeek 版本）
    功能：
    - 统一管理 LLM 调用
    - 标准化输入输出格式
    - 集成日志和错误处理
    """

    def __init__(self, name: str, system_prompt: str):
        """
        :param name: Agent 名称（用于日志标识）
        :param system_prompt: 系统角色设定提示词
        """
        self.name = name
        self.llm = self._init_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}")
        ])

    def _init_llm(self) -> BaseLLM:
        """初始化 DeepSeek LLM"""
        if not settings.DEEPSEEK_API_KEY:
            raise ValueError("未配置 DEEPSEEK_API_KEY")
        return DeepSeekLLM(
            api_key=settings.DEEPSEEK_API_KEY,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS
        )

    def run(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行 Agent 任务
        :param input_data: 输入数据（字符串或字典）
        :return: 标准化输出 {
            "output": str,
            "metadata": dict,
            "error": Optional[str]
        }
        """
        try:
            if isinstance(input_data, dict):
                input_str = str(input_data)
            else:
                input_str = input_data

            # 构造调用链
            chain = self.prompt | self.llm
            response = chain.invoke({"input": input_str})

            self._log_success(input_str, response)
            return {
                "output": response,
                "metadata": {
                    "model": settings.LLM_MODEL,
                    "agent": self.name
                }
            }
        except Exception as e:
            logger.error(f"Agent [{self.name}] 执行失败: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "output": "",
                "metadata": {}
            }

    def _log_success(self, input_data: str, output: str):
        """记录成功日志"""
        logger.info(
            f"\n=== Agent [{self.name}] 执行完成 ===\n"
            f"输入: {input_data[:200]}...\n"
            f"输出: {output[:300]}...\n"
            f"模型: {settings.LLM_MODEL}\n"
            "=" * 50
        )


# 示例化测试
if __name__ == "__main__":
    # 初始化测试 Agent
    test_agent = BaseAgent(
        name="FinancialAnalyst",
        system_prompt="你是一名专业的金融分析师，需用中文回答用户问题"
    )

    # 测试运行
    test_response = test_agent.run({"company": "宁德时代", "question": "当前市盈率是多少？"})
    print(test_response)