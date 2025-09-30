"""
万得(Wind)金融数据API封装：
1. 统一处理认证和错误
2. 提供常用数据接口
"""
import requests
from typing import Dict, List, Optional
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger("wind_connector")

class WindAPI:
    BASE_URL = "https://api.wind.com.cn/data/v3"

    def __init__(self):
        if not Settings.WIND_API_KEY:
            raise ValueError("未配置万得API密钥")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {Settings.WIND_API_KEY}",
            "Content-Type": "application/json"
        })

    def check_connection(self) -> bool:
        """检查API连接状态"""
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/server/ping",
                timeout=5
            )
            return resp.json().get("data") == "pong"
        except Exception as e:
            logger.error(f"万得连接测试失败: {e}")
            return False

    def get_company_financials(self, code: str, fields: List[str] = None) -> Dict:
        """
        获取公司财务数据
        :param code: 证券代码(如: 600030.SH)
        :param fields: 可选字段列表
        :return: {
            "income_statement": {...},
            "balance_sheet": {...},
            "cash_flow": {...}
        }
        """
        default_fields = [
            "oper_revenue", "net_profit", "total_assets",
            "total_liab", "net_cash_flows_oper"
        ]
        params = {
            "codes": code,
            "fields": fields or default_fields,
            "report_type": "all"  # 年报+季报
        }
        try:
            resp = self.session.post(
                f"{self.BASE_URL}/api/fina",
                json=params,
                timeout=10
            )
            data = resp.json()
            if data.get("error_code"):
                raise ValueError(f"万得API错误: {data['error_msg']}")
            return self._normalize_financials(data["data"])
        except Exception as e:
            logger.error(f"财务数据获取失败 {code}: {e}")
            return {}

    def _normalize_financials(self, raw_data: Dict) -> Dict:
        """标准化财务数据结构"""
        return {
            "income_statement": {
                "revenue": raw_data.get("oper_revenue"),
                "net_profit": raw_data.get("net_profit")
            },
            "balance_sheet": {
                "total_assets": raw_data.get("total_assets"),
                "total_liabilities": raw_data.get("total_liab")
            },
            "cash_flow": {
                "net_cash_flow": raw_data.get("net_cash_flows_oper")
            }
        }

    def get_real_time_quotes(self, codes: List[str]) -> Dict[str, float]:
        """获取实时行情"""
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/api/market",
                params={"codes": ",".join(codes)},
                timeout=5
            )
            return {
                item["code"]: item["last_price"]
                for item in resp.json()["data"]
            }
        except Exception as e:
            logger.error(f"行情获取失败 {codes}: {e}")
            return {}