from langsmith import Client
from config.settings import Settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentMonitor:
    def __init__(self):
        self.client = Client(api_key=Settings.LANGSMITH_API_KEY)
        self.project_name = f"financial_agent_{datetime.now().strftime('%Y%m')}"

    def log_run(self, agent_name: str, inputs: dict, outputs: dict, tags: list = None):
        """记录Agent运行轨迹到LangSmith"""
        try:
            self.client.create_run(
                project_name=self.project_name,
                name=agent_name,
                inputs=inputs,
                outputs=outputs,
                tags=tags or [],
                metadata={
                    "env": "production",
                    "llm_model": Settings.LLM_MODEL
                }
            )
        except Exception as e:
            logger.error(f"LangSmith记录失败: {e}")

    def get_agent_stats(self, agent_name: str, days: int = 7):
        """获取Agent历史运行指标"""
        runs = self.client.list_runs(
            project_name=self.project_name,
            execution_order=1,
            start_time=datetime.now() - timedelta(days=days),
            filters={"tags": {"eq": agent_name}}
        )
        return {
            "total_runs": len(runs),
            "avg_latency": sum(r.latency for r in runs)/len(runs) if runs else 0
        }

# 单例模式
monitor = AgentMonitor()