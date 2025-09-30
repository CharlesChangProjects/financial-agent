from .base_agent import BaseAgent
from typing import Dict, List
import logging
import yaml
from config.settings import Settings
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate

# 加载审查专用提示词
with open("config/prompts/review_agent.yaml") as f:
    prompt_config = yaml.safe_load(f)


class ReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="风控审查Agent",
            system_prompt=prompt_config["system_prompt"]
        )
        self.tools = [
            self._check_financial_consistency,
            self._verify_data_sources,
            self._assess_risk_level
        ]

    @tool
    def _check_financial_consistency(self, report: str) -> Dict:
        """检查财务数据内在逻辑一致性（如现金流量表与资产负债表勾稽关系）"""
        # 示例校验规则（实际应更复杂）
        checks = {
            "revenue_growth_vs_profit": "收入增长率>利润增长率时需标注风险",
            "cash_flow_positive": "经营活动现金流必须为正数",
            "debt_ratio_threshold": "资产负债率超过70%需警告"
        }
        return {"checks": checks, "status": "pending"}

    @tool
    def _verify_data_sources(self, metadata: List[Dict]) -> Dict:
        """验证报告中引用的数据来源是否可信"""
        trusted_sources = ["Wind", "S&P Capital IQ", "公司年报"]
        missing_sources = []
        for item in metadata:
            if item.get("source") not in trusted_sources:
                missing_sources.append(item)
        return {
            "trusted_sources_ratio": f"{(len(metadata) - len(missing_sources)) / len(metadata):.0%}",
            "untrusted_items": missing_sources
        }

    @tool
    def _assess_risk_level(self, report: str) -> str:
        """根据报告内容生成风险等级评估"""
        risk_keywords = {
            "high": ["亏损", "下滑", "诉讼", "退市"],
            "medium": ["波动", "放缓", "竞争加剧"],
            "low": ["增长", "稳健", "领先"]
        }
        risk_score = 0
        for level, keywords in risk_keywords.items():
            if any(kw in report for kw in keywords):
                risk_score += {"high": 3, "medium": 2, "low": 1}[level]
        return "高风险" if risk_score >= 4 else "中风险" if risk_score >= 2 else "低风险"

    def review_report(self, research_report: Dict) -> Dict:
        """执行完整审查流程"""
        executor = self.create_executor(self.tools)
        result = executor.invoke({
            "input": f"审查以下分析报告：\n{research_report['content']}",
            "metadata": research_report.get("metadata", [])
        })

        # 生成结构化审查报告
        review_result = {
            "original_report": research_report["content"],
            "risk_level": self._assess_risk_level(result["output"]),
            "data_issues": self._check_financial_consistency(research_report["content"]),
            "suggestions": result["output"]
        }
        self.log_run(research_report["content"], review_result)
        return review_result