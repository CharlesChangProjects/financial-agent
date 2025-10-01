# financial-agent
项目目录结构
financial_agent/
├── config/                        # 配置文件
│   ├── __init__.py
│   ├── settings.py                # 全局参数（API keys、路径等）
│   └── prompts/                   # 预定义提示词模板
│       ├── research_agent.yaml
│       └── report_agent.yaml
├── data/                          # 数据存储
│   ├── raw/                       # 原始数据（PDF/HTML）
│   ├── processed/                 # 清洗后数据
│   └── vector_db/                 # 向量数据库存储路径
├── docs/                          # 项目文档
│   ├── ARCHITECTURE.md            # 架构设计图
│   └── API_REFERENCES.md          # 万得API文档
├── agents/                        # Agent核心模块
│   ├── __init__.py
│   ├── base_agent.py              # 基础Agent类（继承LangChain Agent）
│   ├── research_agent.py          # 行业研究Agent
│   ├── review_agent.py            # 风控校验Agent
│   └── crew_setup.py              # 多Agent协作编排
├── tools/                         # 自定义工具
│   ├── __init__.py
│   ├── wind_tools.py              # 万得API封装
│   └── digikey_tools.py           # 爬虫数据工具
├── knowledge_base/                # RAG知识库系统
│   ├── loader.py                  # 文档加载器（PDF/HTML）
│   ├── splitter.py                # 文本分割策略
│   └── retriever.py               # 检索增强逻辑
├── evaluation/                    # 监控与评估
│   ├── monitor.py                 # LangSmith集成
│   └── metrics.py                 # 自定义评估指标
├── scripts/                       # 实用脚本
│   ├── deploy_vectordb.py         # 知识库初始化脚本
│   └── digikey_scraper.py         # 爬虫脚本
├── app.py                         # FastAPI主应用
└── tests/                         # 单元测试
    ├── test_agents/
    └── test_tools/