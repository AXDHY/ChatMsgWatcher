import httpx

from app.db.dao.groups_dao import query_qq_group_list, save_qq_group_list
from app.services.schemas import QQGroupResponse
from app.services.server_api import QQ_BOT_LOCAL_BASE_URL
from app.services.api import API_GET_GROUP_LIST, API_POST_GROUP_MEMBER_LIST
from app.services.exception import CustomServiceError


class QQGroupService:

    timeout = httpx.Timeout(10.0, connect=5.0, read=5.0)

    @staticmethod
    async def get_group_list():
        url = f"{QQ_BOT_LOCAL_BASE_URL}{API_GET_GROUP_LIST}"
        async with httpx.AsyncClient(timeout=QQGroupService.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                group_reponse = QQGroupResponse.model_validate(response.json())
                return group_reponse.data
            except httpx.HTTPStatusError as e:
                raise CustomServiceError(f"获取群列表失败: {e.response.status_code}")

    @staticmethod
    async def save_group_list():
        group_list = await QQGroupService.get_group_list()
        await save_qq_group_list(group_list)
        return group_list

    @staticmethod
    async def fetch_group_member_list(group_id: int):
        url = f"{QQ_BOT_LOCAL_BASE_URL}{API_POST_GROUP_MEMBER_LIST}"
        payload = {"group_id": group_id, "no_cache": False}
        async with httpx.AsyncClient(timeout=QQGroupService.timeout) as client:
            try:
                response = await client.post(url, data=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise CustomServiceError(
                    f"获取群成员列表失败: {e.response.status_code}"
                )

    @staticmethod
    async def save_group_member_list():
        group_member_list = await QQGroupService.fetch_group_member_list()
        # await save_qq_group_member_list(group_member_list)
        return group_member_list

    @staticmethod
    async def get_group_data_from_local_db(group_id: str):
        result = await query_qq_group_list(group_id=group_id)
        if not result:
            raise CustomServiceError(f"群组信息不存在: {group_id}")
        return result

    @staticmethod
    async def get_group_data_from_server(group_id: str):
        await QQGroupService.get_group_list()
        result = await QQGroupService.get_group_data_from_local_db(group_id)
        if not result:
            raise CustomServiceError(f"群组信息不存在: {group_id}")
        return result

    @staticmethod
    async def get_group_data(group_id: str):
        try:
            result = await QQGroupService.get_group_data_from_local_db(group_id)
            return result
        except CustomServiceError as e:
            result = await QQGroupService.get_group_data_from_server(group_id)
            return result
