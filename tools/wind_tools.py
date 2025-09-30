from langchain.tools import tool
from config.settings import Settings
import requests
import logging

logger = logging.getLogger(__name__)

class WindAPI:
    BASE_URL = "https://api.wind.com/data/v1"

    @staticmethod
    def query(endpoint: str, params: dict):
        headers = {"Authorization": f"Bearer {Settings.WIND_API_KEY}"}
        response = requests.get(
            f"{WindAPI.BASE_URL}/{endpoint}",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

@tool
def get_company_financials(company_code: str) -> dict:
    """获取公司三大财务报表数据"""
    try:
        data = WindAPI.query("company/financials", {"code": company_code})
        return {
            "balance_sheet": data["balance"],
            "income_statement": data["income"],
            "cash_flow": data["cashflow"]
        }
    except Exception as e:
        logger.error(f"Wind API调用失败: {e}")
        return {"error": "财务数据获取失败"}