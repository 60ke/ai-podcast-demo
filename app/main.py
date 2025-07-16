from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import podcast

from app.db.database import init_db


from fastapi.middleware.cors import CORSMiddleware

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await init_db()
#     start_scheduler()
#     yield
    # 可在此处关闭数据库连接、调度器等

# app = FastAPI(title="AI播客生成服务", lifespan=lifespan)
app = FastAPI(title="AI播客生成服务")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# JWT中间件
# app.add_middleware(JWTAuthMiddleware)

# 注册路由
app.include_router(podcast.router, prefix="/podcast", tags=["Podcast"])

@app.get("/")
async def root():
    return {"message": "AI播客生成后端服务已启动"}
