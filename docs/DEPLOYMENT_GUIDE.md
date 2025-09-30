# 部署指南

## 1. 基础环境
```bash
# 安装依赖
pip install -r requirements.txt

# 环境变量配置
export WIND_API_KEY="your_key"
export LANGSMITH_API_KEY="your_key"
```

## 2. 知识库初始化
```bash
python scripts/deploy_vectordb.py \
  --data_dir ./data/raw \
  --vector_db ./data/vector_db
```