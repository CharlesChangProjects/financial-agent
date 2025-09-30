#!/usr/bin/env python3
"""
Digi-Key元器件数据爬虫：
1. 通过产品型号爬取详情页
2. 提取关键参数
3. 存储为结构化JSON
"""
import json
from bs4 import BeautifulSoup
import requests
from utils.logger import setup_logger
from pathlib import Path
from config.settings import Settings

logger = setup_logger("digikey_scraper")

def scrape_part(part_number: str, save_dir: str) -> dict:
    """爬取单个元器件数据"""
    url = f"https://www.digikey.com/en/products/detail/{part_number}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        data = {
            "part_number": part_number,
            "manufacturer": soup.select_one(".manufacturer").text.strip(),
            "description": soup.select_one(".product-description").text.strip(),
            "stock": soup.select_one(".stock").text.strip(),
            "price": soup.select_one(".price").text.strip(),
            "specs": {
                row.select_one(".attr-name").text: row.select_one(".attr-value").text
                for row in soup.select(".specs-table tr")
            }
        }

        # 保存结果
        save_path = Path(save_dir) / f"{part_number}.json"
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"已保存: {save_path}")
        return data
    except Exception as e:
        logger.error(f"爬取失败 {part_number}: {e}")
        return {}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("part_numbers", nargs="+", help="产品型号列表")
    parser.add_argument("--save_dir", default=f"{Settings.DATA_DIR}/raw/digikey", help="存储目录")
    args = parser.parse_args()

    Path(args.save_dir).mkdir(parents=True, exist_ok=True)
    for pn in args.part_numbers:
        scrape_part(pn, args.save_dir)