from datetime import datetime
import pytz

from typing import List
from app.models.QQMessage import QQMessage
from app.models.QQSender import QQSender

beijing_tz = pytz.timezone("Asia/Shanghai")


async def get_earliest_msg_seq(group_id: int) -> int | None:
    earliest_message = (
        await QQMessage.filter(group_id=group_id).order_by("message_seq").first()
    )
    return earliest_message.message_seq if earliest_message else None


async def get_latest_msg_seq(group_id: int) -> int | None:
    latest_message = (
        await QQMessage.filter(group_id=group_id).order_by("-message_seq").first()
    )
    return latest_message.message_seq if latest_message else None


async def save_qq_message_list(msg_list: List[QQMessage]) -> None:
    failed_messages = []  # 用于存储插入失败的记录
    bulk_override = False  # 是否启用批量覆盖

    # 尝试插入数据
    for data in msg_list:
        # 调用封装的检查和更新函数
        needs_update_or_insert = await check_message_data_exist(data)
        if not needs_update_or_insert:
            continue

        sender, created = await QQSender.get_or_create(
            user_id=data.sender.user_id,
            group_id=data.group_id,
            defaults={
                "nickname": data.sender.nickname,
                "card": data.sender.card,
                "role": data.sender.role,
                "title": data.sender.title,
            },
        )

        try:
            await QQMessage.create(
                self_id=data.self_id,
                user_id=data.user_id,
                time=datetime.fromtimestamp(data.time, tz=beijing_tz),
                message_id=data.message_id,
                message_seq=data.message_seq,
                message_type=data.message_type,
                sender=sender,
                raw_message=data.raw_message,
                font=data.font,
                sub_type=data.sub_type,
                message_format=data.message_format,
                post_type=data.post_type,
                group_id=data.group_id,
                message=data.message,
            )
        except Exception as e:
            # print(f"插入失败: {e}")
            failed_messages.append(data)

    if failed_messages:
        # 如果有失败的记录，询问用户是否批量覆盖
        user_input = (
            input(f"共 {len(failed_messages)} 条记录插入失败，是否全部覆盖？(y/n): ")
            .strip()
            .lower()
        )

        if user_input == "y":
            bulk_override = True
            print("已选择覆盖所有失败的记录")
        else:
            print("未执行覆盖操作，跳过所有失败记录")

    # 批量覆盖后续所有失败记录
    if bulk_override:
        for data in failed_messages:
            sender, created = await QQSender.get_or_create(
                user_id=data.sender.user_id,
                group_id=data.group_id,
                defaults={
                    "nickname": data.sender.nickname,
                    "card": data.sender.card,
                    "role": data.sender.role,
                    "title": data.sender.title,
                },
            )

            try:
                await QQMessage.filter(
                    message_id=data.message_id, message_seq=data.message_seq
                ).update(
                    self_id=data.self_id,
                    user_id=data.user_id,
                    time=datetime.fromtimestamp(data.time, tz=beijing_tz),
                    message_type=data.message_type,
                    sender=sender,
                    raw_message=data.raw_message,
                    font=data.font,
                    sub_type=data.sub_type,
                    message_format=data.message_format,
                    post_type=data.post_type,
                    group_id=data.group_id,
                    message=data.message,
                )
                print(f"记录 [{data.message_seq}] {data.message_id} 已覆盖")
            except Exception as e:
                print(f"覆盖记录 [{data.message_seq}] {data.message_id} 失败: {e}")


async def check_message_data_exist(message: QQMessage) -> bool:
    """
    检查消息记录是否已经存在，并详细记录不一致的字段
    :param message: 消息记录
    :return: 如果数据不一致或不存在，返回 True；否则返回 False
    """
    # 检查是否已有记录
    existing_message = await QQMessage.filter(
        message_id=message.message_id, message_seq=message.message_seq
    ).first()

    if existing_message:
        # 获取 QQSender 对象
        existing_sender = await existing_message.sender

        # 检查数据是否完全一致
        if (
            existing_message.self_id == message.self_id
            and existing_message.user_id == message.user_id
            and existing_message.time
            == datetime.fromtimestamp(message.time, tz=beijing_tz)
            and existing_message.message_type == message.message_type
            and existing_sender.user_id == message.sender.user_id
            and existing_message.raw_message == message.raw_message
            and existing_message.font == message.font
            and existing_message.sub_type == message.sub_type
            and existing_message.message_format == message.message_format
            and existing_message.post_type == message.post_type
            and existing_message.group_id == message.group_id
            and existing_message.message == message.message
        ):
            print(f"记录 [{message.message_seq}] {message.message_id} 已存在，跳过插入")
            return False  # 数据一致，跳过插入
        else:
            # 记录不一致，详细记录不一致的字段
            discrepancies = []
            if existing_message.self_id != message.self_id:
                discrepancies.append(
                    f"self_id: {existing_message.self_id} -> {message.self_id}"
                )
            if existing_message.user_id != message.user_id:
                discrepancies.append(
                    f"user_id: {existing_message.user_id} -> {message.user_id}"
                )
            if existing_message.time != datetime.fromtimestamp(message.time, tz=beijing_tz):
                discrepancies.append(
                    f"time: {existing_message.time} -> {datetime.fromtimestamp(message.time, tz=beijing_tz)}"
                )
            if existing_message.message_type != message.message_type:
                discrepancies.append(
                    f"message_type: {existing_message.message_type} -> {message.message_type}"
                )
            if existing_sender.user_id != message.sender.user_id:
                discrepancies.append(
                    f"sender_user_id: {existing_sender.user_id} -> {message.sender.user_id}"
                )
            if existing_message.raw_message != message.raw_message:
                discrepancies.append(
                    f"raw_message: {existing_message.raw_message} -> {message.raw_message}"
                )
            if existing_message.font != message.font:
                discrepancies.append(
                    f"font: {existing_message.font} -> {message.font}"
                )
            if existing_message.sub_type != message.sub_type:
                discrepancies.append(
                    f"sub_type: {existing_message.sub_type} -> {message.sub_type}"
                )
            if existing_message.message_format != message.message_format:
                discrepancies.append(
                    f"message_format: {existing_message.message_format} -> {message.message_format}"
                )
            if existing_message.post_type != message.post_type:
                discrepancies.append(
                    f"post_type: {existing_message.post_type} -> {message.post_type}"
                )
            if existing_message.group_id != message.group_id:
                discrepancies.append(
                    f"group_id: {existing_message.group_id} -> {message.group_id}"
                )
            if existing_message.message != message.message:
                discrepancies.append(
                    f"message: {existing_message.message} -> {message.message}"
                )

            print(
                f"记录 [{message.message_seq}] {message.message_id} 存在，但数据不一致，准备更新。不一致的字段: {', '.join(discrepancies)}"
            )
            # 数据不一致，返回需要更新的标志
            return True
    else:
        # 记录不存在，返回需要插入的标志
        return True
