#!/usr/bin/env python3
"""
自动生成API参考文档：
1. 扫描tools/agents目录
2. 提取函数docstring
3. 生成Markdown文档
"""
from pathlib import Path
import inspect
from utils.logger import setup_logger

logger = setup_logger("generate_docs")


def extract_tool_docs(module_path: str) -> str:
    """从Python模块提取工具文档"""
    docs = []
    module_name = Path(module_path).stem
    module = __import__(f"tools.{module_name}", fromlist=["*"])

    for name, obj in inspect.getmembers(module):
        if hasattr(obj, "__tool_metadata__"):
            docs.append(f"### {name}\n```python\n{inspect.getdoc(obj)}\n```")
    return "\n\n".join(docs)


def generate_api_reference():
    """生成API参考文档"""
    output_path = Path("docs/API_REFERENCES.md")
    content = ["# API 参考手册\n"]

    for tool_file in Path("tools").glob("*.py"):
        if tool_file.stem == "__init__":
            continue
        docs = extract_tool_docs(tool_file.stem)
        if docs:
            content.append(f"## {tool_file.stem}\n{docs}")

    output_path.write_text("\n\n".join(content))
    logger.info(f"已生成API文档: {output_path}")


if __name__ == "__main__":
    generate_api_reference()