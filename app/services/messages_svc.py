import httpx

from app.services.schemas import QQMessageResponse
from app.services.server_api import QQ_BOT_LOCAL_BASE_URL
from app.services.api import API_POST_GROUP_MSG_HISTORY
from app.services.exception import CustomServiceError
from app.db.dao.messages_dao import (
    get_earliest_msg_seq,
    save_qq_message_list,
    get_latest_msg_seq,
)


class QQMessageService:

    timeout = httpx.Timeout(10.0, connect=5.0, read=5.0)

    @staticmethod
    async def sync_messages(group_id: int, last_seq_id: int = 0, limit: int = 100):
        url = f"{QQ_BOT_LOCAL_BASE_URL}{API_POST_GROUP_MSG_HISTORY}"
        payload = {
            "group_id": group_id,
            "message_seq": last_seq_id,
            "count": limit,
        }
        async with httpx.AsyncClient(timeout=QQMessageService.timeout) as client:
            try:
                response = await client.post(url, data=payload)
                response.raise_for_status()
                msg_response = QQMessageResponse.model_validate(response.json())
                return msg_response.data.messages
            except httpx.HTTPStatusError as e:
                raise CustomServiceError(
                    f"获取群历史消息失败: {e.response.status_code}"
                )

    @staticmethod
    async def save_messages(group_id: int, last_seq_id: int = 0, limit: int = 100):
        last_seq_id_db = await get_latest_msg_seq(group_id)
        earliest_seq_id_db = await get_earliest_msg_seq(group_id)

        msg_response = await QQMessageService.sync_messages(
            group_id, last_seq_id, limit
        )

        earliest_seq_id_online = msg_response[0].message_seq if msg_response else None
        last_seq_id_online = msg_response[-1].message_seq if msg_response else None

        if not last_seq_id_online:
            print(f"群 {group_id} 没有历史消息")
            return msg_response
        if (
            last_seq_id_db
            and last_seq_id_db >= last_seq_id_online
            and earliest_seq_id_online > earliest_seq_id_db
        ):
            print(f"群 {group_id} 没有新消息以及更早的历史消息")
            return msg_response

        if earliest_seq_id_db and earliest_seq_id_online < earliest_seq_id_db:
            print(f"群 {group_id} 历史有更早的消息需要同步")
        if not last_seq_id_db:
            print(f"数据库中没有群 {group_id} 消息")
            last_seq_id = 0
            last_seq_id_db = last_seq_id_online - limit
        if last_seq_id_online - last_seq_id_db > limit:
            limit_new = last_seq_id_online - last_seq_id_db
            print(f"群 {group_id} 新消息数量超过 {limit_new} 条，需要重新请求同步")
            msg_response = await QQMessageService.sync_messages(
                group_id, last_seq_id_online, limit_new
            )
        await save_qq_message_list(msg_response)
        return msg_response
