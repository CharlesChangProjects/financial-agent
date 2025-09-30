# API 参考手册

## 万得API封装
```python
@tool
def get_wind_financials(company_code: str):
    """
    获取公司三大报表数据
    :param company_code: 万得公司代码(如: 300750.SZ)
    :return: {
        "balance_sheet": {...},
        "income_statement": {...},
        "cash_flow": {...}
    }
    """
```

## 内部REST接口
`POST /analyze`
```json
{
  "company": "宁德时代",
  "industry": "新能源",
  "priority": false
}
```