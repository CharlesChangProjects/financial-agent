from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import logging
from typing import Optional, Dict, Any
import os
from config.settings import Settings
# 初始化FastAPI应用
app = FastAPI(
    title="金融分析智能体API",
    description="提供公司行业分析报告的AI智能体服务",
    version="1.0.0"
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 数据模型
class AnalysisRequest(BaseModel):
    company: str
    industry: str
    priority: Optional[str] = "normal"
    deadline: Optional[str] = None


class AnalysisResponse(BaseModel):
    status: str
    report: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Any]
    error: Optional[str] = None


def check_knowledge_initialized():
    from chromadb import PersistentClient
    client = PersistentClient(path=Settings.VECTOR_DB_PATH)
    if not client.list_collections():
        raise RuntimeError("知识库未初始化！请先运行 scripts/deploy_vectordb.py")

@app.on_event("startup")
async def startup():
    check_knowledge_initialized()
    logger.info("知识库验证通过")

# 初始化Crew（延迟导入避免LLM配置冲突）
def initialize_crew():
    """延迟初始化Crew以正确处理LLM配置"""
    from agents.crew_setup import crew

    # 确保LLM配置正确
    for agent in crew.agents:
        if hasattr(agent, 'llm'):
            if isinstance(agent.llm, str):
                if agent.llm.lower() == "deepseek":
                    agent.llm = {
                        "model": "deepseek-chat",
                        "api_key": os.getenv("DEEPSEEK_API_KEY"),
                        "base_url": "https://api.deepseek.com/v1"
                    }
                    logger.info(f"已配置DeepSeek模型: {agent.role}")

    return crew


# 全局crew实例（延迟初始化）
_crew = None


def get_crew():
    global _crew
    if _crew is None:
        _crew = initialize_crew()
    return _crew


# 健康检查端点
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "OK"}


# 核心分析端点
@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"description": "内部服务器错误"},
        400: {"description": "无效输入参数"}
    }
)
async def analyze_company(request: AnalysisRequest):
    """执行公司行业分析"""
    result = {
        "status": "success",
        "report": None,
        "metrics": {
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_sec": None
        },
        "error": None
    }

    try:
        # 验证输入
        if not request.company or not request.industry:
            raise HTTPException(
                status_code=400,
                detail="公司和行业参数不能为空"
            )

        logger.info(f"开始分析 {request.company} ({request.industry})")

        # 获取已正确配置的crew实例
        crew = get_crew()

        # 构建输入参数
        inputs = {
            "company": request.company,
            "industry": request.industry,
            "crewai_trigger_payload": {
                "priority": request.priority,
                "deadline": request.deadline
            }
        }

        # 执行分析
        analysis_report = crew.kickoff(inputs=inputs)

        # 处理结果
        result["report"] = {
            "summary": analysis_report[:500],  # 截断长文本
            "full_report": analysis_report if len(analysis_report) <= 2000 else None
        }

        logger.info(f"分析完成: {request.company}")

    except HTTPException:
        raise  # 直接传递已处理的HTTP异常
    except Exception as e:
        logger.error(f"分析失败: {str(e)}", exc_info=True)
        result["status"] = "error"
        result["error"] = str(e)
    finally:
        # 计算耗时
        end_time = datetime.now()
        result["metrics"]["end_time"] = end_time.isoformat()
        start_time = datetime.fromisoformat(result["metrics"]["start_time"])
        result["metrics"]["duration_sec"] = round(
            (end_time - start_time).total_seconds(), 2
        )

    # 根据状态返回不同HTTP状态码
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "分析过程中发生错误",
                "error": result["error"],
                "metrics": result["metrics"]
            }
        )

    return result


# 启动配置
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        timeout_keep_alive=60
    )