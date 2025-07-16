# AI播客生成全栈项目

本项目包含：
- **后端服务**：基于 FastAPI + LangChain + MySQL，支持多LLM服务商，播客内容生成与管理。
- **前端应用**：基于 Next.js + TailwindCSS，提供现代化的播客生成与管理界面。


## ai播客工具和市场分析



## 依赖安装
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## 启动方式
```bash
# must export DATABASE_DSN,OPENAI_API_KEY
uvicorn app.main:app --reload
``` 

## 接口文档
`http://localhost:8000/docs`

# 项目目录结构说明

```
homework-bg/
├── app/                       # 后端主目录
│   ├── __init__.py
│   ├── api/                  # FastAPI 路由与接口定义
│   ├── core/                 # 配置、调度与中间件
│   ├── db/                   # 数据库相关
│   ├── llm_providers/        # 大模型相关实现
│   ├── main.py               # FastAPI 应用入口
│   ├── models/               # ORM模型
│   ├── schemas/              # Pydantic数据结构
│   ├── services/             # 业务逻辑
│   └── tasks/                # 任务相关（如有）
├── frontend/                  # 前端主目录（Next.js项目）
│   ├── src/                  # 前端源码
│   ├── public/               # 静态资源
│   ├── package.json          # 前端依赖
│   ├── tsconfig.json         # TypeScript配置
│   ├── tailwind.config.ts    # TailwindCSS配置
│   ├── next.config.js        # Next.js配置
│   └── ...                   # 其他前端相关文件
├── README.md                 # 项目说明文档
├── requirements.txt          # Python依赖
```

## 主要目录说明
- **app/**：后端服务主目录，见下方详细说明。
- **frontend/**：前端应用主目录，基于 Next.js + TailwindCSS，负责UI交互与API对接。
- **README.md**：项目说明文档。
- **requirements.txt**：后端依赖。

### 后端(app/)结构简述
- **api/**：接口路由层，定义所有API入口。
- **core/**：全局配置、调度、认证等核心功能。
- **db/**：数据库连接与初始化。
- **llm_providers/**：大模型（如OpenAI、Azure等）相关的调用与适配。
- **models/**：SQLAlchemy ORM模型，定义数据库表结构。
- **schemas/**：Pydantic数据结构，定义接口请求/响应格式。
- **services/**：业务逻辑实现，处理具体的功能需求。
- **tasks/**：异步任务、定时任务相关代码（如有）。
- **main.py**：FastAPI应用启动入口。

### 前端(frontend/)结构简述
- **src/**：前端主要源码，页面、组件、hooks等。
- **public/**：静态资源（图片、icon等）。
- **package.json**：前端依赖管理。
- **tsconfig.json**：TypeScript配置。
- **tailwind.config.ts**：TailwindCSS配置。
- **next.config.js**：Next.js配置。


## 前后端启动说明
1. **后端**：见上方“依赖安装/启动方式”
2. **前端**：
   ```bash
   cd frontend
   npm install # 或 yarn 或 bun install
   npm run dev # 或 yarn dev 或 bun dev
   ```
   默认前端开发服务器地址为 `http://localhost:3000`


