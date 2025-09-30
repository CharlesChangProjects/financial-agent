from crewai import Agent, Task, Crew
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import logging
from crewai.tools import tool
from datetime import datetime

logger = logging.getLogger(__name__)


# ----------------------------
# 工具定义（严格遵循BaseTool规范）
# ----------------------------
class QueryKnowledgeBaseInput(BaseModel):
    question: str = Field(..., description="要查询的问题")


class FetchFinancialDataInput(BaseModel):
    company_code: str = Field(..., description="公司股票代码")


@tool
def query_knowledge_base(question: str) -> List[Dict]:
    """查询知识库工具

    Args:
        question (str): 要查询的问题

    Returns:
        List[Dict]: 查询结果列表
    """
    from knowledge_base.retriever import retriever
    return retriever.query(question)


@tool
def fetch_financial_data(company_code: str) -> Dict:
    """获取公司财务数据工具

    Args:
        company_code (str): 公司股票代码

    Returns:
        Dict: 财务数据字典
    """
    from tools.wind_tools import get_company_financials
    return get_company_financials(company_code)


# 设置工具属性
query_knowledge_base.result_as_answer = True
query_knowledge_base.max_usage_count = 10


# ----------------------------
# 创建Agent和Crew（完全兼容Task类规范）
# ----------------------------
def setup_agents_and_crew() -> Crew:
    # 定义Agents（包含所有必填字段）
    research_agent = Agent(
        role="行业研究员",
        goal="生成准确的行业分析报告",
        backstory="资深金融分析师，擅长挖掘行业数据",
        tools=[query_knowledge_base, fetch_financial_data],
        verbose=True,
        allow_delegation=False,
        max_iter=15,
        max_rpm=10,
        llm="deepseek",
        allow_code_execution=False,
        respect_context_window=True
    )

    review_agent = Agent(
        role="风控专家",
        goal="确保报告数据准确性",
        backstory="前四大会计师事务所审计师",
        tools=[query_knowledge_base],
        verbose=True,
        max_iter=15,
        max_rpm=10,
        llm="deepseek",
        allow_code_execution=False
    )

    # 定义Tasks（完整参数配置）
    research_task = Task(
        description="分析{company}在{industry}行业的表现",
        expected_output="完整的Markdown格式分析报告",
        agent=research_agent,
        human_input=False,
        output_json=None,
        output_pydantic=None,
        output_file=None,
        create_directory=True,
        async_execution=False,
        config={
            "temperature": 0.3,
            "max_tokens": 2000
        },
        guardrail="报告必须包含财务数据验证部分",
        guardrail_max_retries=3
    )

    review_task = Task(
        description="校验报告中的财务数据异常",
        expected_output="风险点清单及修正建议",
        agent=review_agent,
        context=[research_task],
        human_input=False,
        output_json=None,
        output_pydantic=None,
        markdown=True,
        inject_date=True,
        date_format="%Y-%m-%d"
    )

    # 创建Crew（完整参数）
    crew = Crew(
        agents=[research_agent, review_agent],
        tasks=[research_task, review_task],
        process="sequential",
        memory=False,
        embedder=None,
        full_output=False
    )

    return research_agent, review_agent, crew


# 单例模式
research_agent, review_agent, crew = setup_agents_and_crew()

