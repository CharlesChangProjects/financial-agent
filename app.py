from fastapi import FastAPI
from agents.crew_setup import research_agent, review_agent
from pydantic import BaseModel

app = FastAPI()

class AnalysisRequest(BaseModel):
    company: str
    industry: str

@app.get("/")
def home():
    return {"status": "OK", "message": "Financial Agent API"}

class AnalysisPipeline:
    @staticmethod
    def run(company: str, industry: str):
        # 步骤1：研究分析
        research_output = research_agent.run(
            input=f"请分析{company}在{industry}行业的表现",
            tools=["query_knowledge_base"]
        )

        # 步骤2：风险审核
        review_output = review_agent.run(
            input=f"请审核{company}的财务风险",
            context=research_output,
            tools=["fetch_financial_data"]
        )

        return review_output


@app.post("/analyze")
async def analyze(company: str, industry: str):
    return AnalysisPipeline.run(company, industry)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)