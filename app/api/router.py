from fastapi import APIRouter
from app.api.v1 import groups  # 导入子模块路由

api_router = APIRouter()

# 注册各模块的路由
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
