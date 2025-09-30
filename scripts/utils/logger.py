"""
日志配置工具
"""
import logging
from pathlib import Path
from config.settings import Settings

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """配置统一格式的日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 控制台输出
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # 文件输出
    log_dir = Path(Settings.DATA_DIR) / "logs"
    log_dir.mkdir(exist_ok=True)
    fh = logging.FileHandler(log_dir / f"{name}.log")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger