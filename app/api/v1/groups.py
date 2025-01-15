from fastapi import APIRouter
from app.services.groups_svc import QQGroupService

router = APIRouter()


@router.get("/test", summary="test")
async def test():
    return {"message": "Hello World"}


@router.get("/qq_group_list", summary="获取QQ群列表")
async def get_qq_group_list():
    group_list = await QQGroupService.save_group_list()
    return group_list


@router.get("/qq_group_member_list", summary="获取指定QQ群成员列表")
async def get_qq_group_member_list(group_id):
    group_list = await QQGroupService.get_group_data(group_id)
    if not group_list:
        return
    result = await QQGroupService.fetch_group_member_list(group_list[0].group_id)
    return result
