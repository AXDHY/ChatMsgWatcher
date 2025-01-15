from fastapi import APIRouter
from app.services.groups_svc import QQGroupService
from app.services.messages_svc import QQMessageService

router = APIRouter()


@router.get("/test", summary="test")
async def test():
    return {"message": "Hello World"}


@router.get("/qq_group_list", summary="获取QQ群列表")
async def get_qq_group_list():
    group_list = await QQGroupService.save_group_list()
    return group_list


@router.get("/qq_group_member_list", summary="获取指定QQ群成员列表")
async def get_qq_group_member_list(group_id: int):
    group_list = await QQGroupService.get_group_data(group_id)
    if not group_list:
        return
    result = await QQGroupService.fetch_group_member_list(group_list[0].group_id)
    return result


@router.get("/qq_group_msg_history", summary="获取指定QQ群历史消息")
async def get_qq_group_msg_history(group_id: int, limit: int = 100):
    history_msg = await QQMessageService.save_messages(group_id, limit=limit)
    if not history_msg:
        return
    return history_msg
