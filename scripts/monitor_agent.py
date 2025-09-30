#!/usr/bin/env python3
"""
Agent性能监控脚本：
1. 实时采集CPU/内存使用率
2. 记录LangSmith运行轨迹
3. 触发异常报警
"""
import psutil
import time
from datetime import datetime
from typing import Dict, Optional
from config.settings import Settings
from evaluation.monitor import monitor
from utils.logger import setup_logger
from utils.wind_connector import WindAPI

logger = setup_logger("monitor_agent")


class AgentMonitor:
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.wind = WindAPI() if Settings.WIND_API_KEY else None

    def get_system_metrics(self) -> Dict:
        """获取系统级监控指标"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }

    def check_agent_health(self, agent_name: str) -> Optional[Dict]:
        """检查指定Agent的健康状态"""
        try:
            stats = monitor.get_agent_stats(agent_name)
            if stats["avg_latency"] > 5000:  # 超过5秒延迟视为异常
                self.trigger_alert(f"{agent_name} 响应延迟过高: {stats['avg_latency']}ms")
            return stats
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return None

    def trigger_alert(self, message: str):
        """触发分级报警"""
        if "CRITICAL" in message:
            self._send_sms_alert(message)
        logger.error(f"ALERT: {message}")
        # 可扩展：Slack/邮件通知

    def run(self):
        """启动监控循环"""
        logger.info("启动Agent监控服务...")
        while True:
            try:
                metrics = self.get_system_metrics()
                if self.wind:
                    metrics["wind_api_status"] = self.wind.check_connection()

                # 监控关键Agent
                for agent in ["ResearchAgent", "ReviewAgent"]:
                    agent_stats = self.check_agent_health(agent)
                    if agent_stats:
                        metrics.update({f"{agent}_stats": agent_stats})

                logger.info(f"监控指标: {metrics}")
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                logger.info("监控服务终止")
                break
            except Exception as e:
                logger.critical(f"监控循环异常: {e}")
                time.sleep(10)  # 防止频繁崩溃


if __name__ == "__main__":
    monitor = AgentMonitor(check_interval=300)  # 每5分钟检查一次
    monitor.run()