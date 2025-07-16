import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_DSN = os.getenv("DATABASE_DSN")
# if DATABASE_DSN:
#     DATABASE_URL = DATABASE_DSN
# else:
#     MYSQL_USER = os.getenv("MYSQL_USER", "root")
#     MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
#     MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
#     MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
#     MYSQL_DB = os.getenv("MYSQL_DB", "homework_bg")
#     DATABASE_URL = (
#         f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
#         f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
#     )

engine = create_async_engine(DATABASE_DSN, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    # 可在此处做表结构初始化等
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
