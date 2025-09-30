from langchain.tools import tool
from config.settings import Settings
import matplotlib.pyplot as plt
import io
import base64


class ReportTools:
    @tool
    def generate_chart(data: dict, chart_type: str = "line") -> str:
        """生成基础数据图表并返回Base64编码图像"""
        plt.figure()
        if chart_type == "line":
            plt.plot(data["x"], data["y"])
        elif chart_type == "bar":
            plt.bar(data["labels"], data["values"])
        plt.title(data.get("title", ""))

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

    @tool
    def convert_to_ppt(summary: str) -> str:
        """将报告摘要转换为PPT大纲格式"""
        sections = summary.split("##")
        ppt_lines = []
        for sec in sections:
            if not sec.strip():
                continue
            title, *content = sec.split("\n")
            ppt_lines.append(f"Slide: {title.strip()}")
            ppt_lines.extend(f"  - {line.strip()}" for line in content if line.strip())
        return "\n".join(ppt_lines)