from typing import Dict, List
import numpy as np
from sklearn.metrics import precision_score


class EvaluationMetrics:
    @staticmethod
    def correctness(ground_truth: str, prediction: str) -> float:
        """内容准确性评估（基于文本相似度）"""
        from sentence_transformers import util
        embeddings = Settings.embedding_model.encode([ground_truth, prediction])
        return util.cos_sim(embeddings[0], embeddings[1]).item()

    @staticmethod
    def safety_score(output: str, banned_phrases: List[str]) -> float:
        """安全性评估（敏感词检测）"""
        return 0 if any(phrase in output for phrase in banned_phrases) else 1

    @staticmethod
    def financial_consistency(data: Dict) -> float:
        """财务数据逻辑一致性评分"""
        # 示例：检查资产负债表平衡
        assets = data["balance_sheet"]["total_assets"]
        liabilities = data["balance_sheet"]["total_liabilities"]
        equity = data["balance_sheet"]["total_equity"]
        balance_ok = abs(assets - (liabilities + equity)) < 0.01 * assets

        # 检查现金流量表净现金流与资产负债表现金变化匹配
        cash_flow_ok = (data["cash_flow"]["net_change"] ==
                        data["balance_sheet"]["cash_end"] - data["balance_sheet"]["cash_begin"])

        return 1.0 if balance_ok and cash_flow_ok else 0.5

    @classmethod
    def composite_score(cls, test_cases: List[Dict]) -> Dict:
        """综合评分（加权平均）"""
        scores = {
            "correctness": np.mean([cls.correctness(tc["truth"], tc["pred"]) for tc in test_cases]),
            "safety": np.mean([cls.safety_score(tc["pred"], tc.get("banned", [])) for tc in test_cases]),
            "consistency": np.mean([cls.financial_consistency(tc.get("data", {})) for tc in test_cases])
        }
        scores["overall"] = 0.5 * scores["correctness"] + 0.3 * scores["consistency"] + 0.2 * scores["safety"]
        return scores