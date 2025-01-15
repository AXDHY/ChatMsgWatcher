from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.router import api_router
from app.db.database import db_init, db_close

# 初始化数据库
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db_init()
    yield
    # Shutdown
    await db_close()


app = FastAPI(
    title="MsgWatcher",
    description="Online Chat Software Local Data Monitor, Parser & Saver",
    version="1.0.0",
    lifespan=lifespan
)

# 注册 API 路由
app.include_router(api_router)

# 启动应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
