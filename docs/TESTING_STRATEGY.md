# 测试策略

## 1. 单元测试覆盖率
```bash
# 运行测试
pytest --cov=agents --cov=knowledge_base tests/

# 生成报告
Coverage: 82% (目标≥80%)
```

## 2. 端到端测试用例
```python
def test_full_analysis_flow():
    research = ResearchAgent().run("宁德时代")
    review = ReviewAgent().review_report(research)
    assert "风险提示" in review["output"]
```