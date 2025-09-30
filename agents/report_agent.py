from .base_agent import BaseAgent
from tools.report_tools import ReportTools
import yaml
from typing import Dict

with open("config/prompts/report_agent.yaml") as f:
    prompt_config = yaml.safe_load(f)


class ReportAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="报告生成Agent",
            system_prompt=prompt_config["system_prompt"]
        )
        self.tools = [
            ReportTools().generate_chart,
            ReportTools().convert_to_ppt
        ]

    def generate_reports(self, research_data: Dict, review_comments: Dict) -> Dict:
        """生成多版本报告"""
        executor = self.create_executor(self.tools)

        # 动态提示词构造
        prompt_vars = {
            "research_content": research_data["content"],
            "review_comments": review_comments["suggestions"],
            "is_urgent": research_data.get("priority", False)
        }

        result = executor.invoke({
            "input": prompt_config["system_prompt"],
            **prompt_vars
        })

        return {
            "professional": self._format_report(result["output"], "专业版"),
            "executive": self._extract_summary(result["output"]),
            "investor": self._add_disclaimer(result["output"])
        }

    def _format_report(self, raw: str, version: str) -> str:
        """按版本格式化报告"""
        # 实际实现应更复杂，这里简化为添加版本头
        return f"# {version}报告\n{raw}"

    def _extract_summary(self, report: str) -> str:
        """提取关键点生成高管摘要"""
        import re
        key_points = re.findall(r"【关键结论】(.+?)【详细分析】", report, re.DOTALL)
        return "高管摘要:\n" + ("\n".join(key_points) if key_points else report[:500])

    def _add_disclaimer(self, report: str) -> str:
        """为投资者版添加风险声明"""
        return report + "\n\n---\n*投资有风险，过往业绩不预示未来表现*"