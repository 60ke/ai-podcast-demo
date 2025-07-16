# AI播客生成后端服务

本项目基于 FastAPI + LangChain + MySQL，支持多LLM服务商，异步任务调度与播客内容生成。



## ai播客工具和市场分析




## 依赖安装
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## 启动方式
```bash
uvicorn app.main:app --reload
``` 

## 接口文档
`http://localhost:8000/docs`

# 项目目录结构说明

```
homework-bg/
├── app/
│   ├── __init__.py
│   ├── api/                  # FastAPI 路由与接口定义
│   │   ├── __init__.py
│   │   └── podcast.py
│   ├── core/                 # 配置、调度与中间件
│   │   ├── __init__.py
│   │   ├── config.py         # 配置相关
│   │   ├── jwt_middleware.py # JWT中间件
│   │   └── scheduler.py      # 定时任务
│   ├── db/                   # 数据库相关
│   │   ├── __init__.py
│   │   └── database.py
│   ├── llm_providers/        # 大模型相关实现
│   │   ├── __init__.py
│   │   ├── azure.py
│   │   ├── base.py           # 统一的LLM流式生成逻辑
│   │   └── openai.py
│   ├── main.py               # FastAPI 应用入口
│   ├── models/               # ORM模型
│   │   ├── __init__.py
│   │   └── podcast_task.py
│   ├── schemas/              # Pydantic数据结构
│   │   ├── __init__.py
│   │   └── podcast.py
│   ├── services/             # 业务逻辑
│   │   ├── __init__.py
│   │   └── podcast_service.py
│   └── tasks/                # 任务相关
│       ├── __init__.py
│       └── podcast_task.py
├── README.md                 # 项目说明文档
├── requirements.txt          # Python依赖
```

## 主要目录说明
- **app/api/**：接口路由层，定义所有API入口。
- **app/core/**：全局配置、调度、认证等核心功能。
- **app/db/**：数据库连接与初始化。
- **app/llm_providers/**：大模型（如OpenAI、Azure等）相关的调用与适配。
- **app/models/**：SQLAlchemy ORM模型，定义数据库表结构。
- **app/schemas/**：Pydantic数据结构，定义接口请求/响应格式。
- **app/services/**：业务逻辑实现，处理具体的功能需求。
- **app/tasks/**：异步任务、定时任务相关代码。
- **main.py**：FastAPI应用启动入口。



