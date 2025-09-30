from langchain.tools import tool
from bs4 import BeautifulSoup
import requests


@tool
def get_part_inventory(part_number: str) -> dict:
    """获取Digi-Key元器件的库存和价格"""
    url = f"https://www.digikey.com/en/products/detail/{part_number}"
    try:
        response = requests.get(url, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')

        return {
            "stock": soup.select_one(".stock").text.strip(),
            "price": soup.select_one(".price").text.strip(),
            "lead_time": soup.select_one(".lead-time").text.strip()
        }
    except Exception:
        return {"error": "Digi-Key数据获取失败"}