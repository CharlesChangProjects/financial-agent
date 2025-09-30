from tools.wind_tools import get_company_financials
from .base_agent import BaseAgent
from knowledge_base.retriever import retriever
import yaml

with open("config/prompts/research_agent.yaml") as f:
    prompt_config = yaml.safe_load(f)


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="行业研究Agent",
            system_prompt=prompt_config["system_prompt"]
        )
        self.tools = [
            retriever.query,
            get_company_financials  # 从wind_tools导入
        ]

    def analyze_company(self, company: str, industry: str):
        executor = self.create_executor(self.tools)
        result = executor.invoke({
            "input": f"分析{company}的财务状况",
            "industry": industry
        })
        self.log_run(company, result["output"])
        return result