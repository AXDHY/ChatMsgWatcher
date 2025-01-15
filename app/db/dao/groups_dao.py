from datetime import datetime
from typing import List, Optional

from tortoise.queryset import QuerySet
from app.models.QQgroup import QQGroup
from app.services.schemas import QQGroupInfo
from app.config import beijing_tz


async def save_qq_group_list(group_list: List[QQGroupInfo]):
    failed_groups = []  # 用于存储插入失败的记录
    bulk_override = False  # 是否启用批量覆盖

    # 尝试插入数据
    for group in group_list:
        # 调用封装的检查和更新函数
        needs_update_or_insert = await check_group_data_exist(group)
        if not needs_update_or_insert:
            continue

        try:
            await QQGroup.create(
                group_id=group.group_id,
                group_name=group.group_name,
                group_memo=group.group_memo,
                group_create_time=datetime.fromtimestamp(
                    group.group_create_time, tz=beijing_tz
                ),
                member_count=group.member_count,
                max_member_count=group.max_member_count,
            )
        except Exception as e:
            # print(f"插入失败: {e}")
            failed_groups.append(group)

    if failed_groups:
        # 如果有失败的记录，询问用户是否批量覆盖
        user_input = (
            input(f"共 {len(failed_groups)} 条记录插入失败，是否全部覆盖？(y/n): ")
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
        for group in failed_groups:
            try:
                await QQGroup.filter(group_id=group.group_id).update(
                    group_name=group.group_name,
                    group_memo=group.group_memo,
                    group_create_time=datetime.fromtimestamp(
                        group.group_create_time, tz=beijing_tz
                    ),
                    member_count=group.member_count,
                    max_member_count=group.max_member_count,
                )
                print(f"记录 {group.group_id} {group.group_name} 已覆盖")
            except Exception as e:
                print(f"覆盖记录 {group.group_id} {group.group_name} 失败: {e}")


async def check_group_data_exist(group: QQGroupInfo):
    # 检查是否已有记录
    existing_group = await QQGroup.filter(group_id=group.group_id).first()

    if existing_group:
        # 检查数据是否完全一致
        if (
            existing_group.group_name == group.group_name
            and existing_group.group_memo == group.group_memo
            and existing_group.group_create_time
            == datetime.fromtimestamp(group.group_create_time, tz=beijing_tz)
            and existing_group.member_count == group.member_count
            and existing_group.max_member_count == group.max_member_count
        ):
            print(f"记录 {group.group_id} {group.group_name} 已存在，跳过插入")
            return False  # 数据一致，跳过插入
        else:
            # 记录不一致，详细记录不一致的字段
            discrepancies = ""
            if existing_group.group_name != group.group_name:
                discrepancies = (
                    f"group_name: {existing_group.group_name} -> {group.group_name}"
                )
            if existing_group.group_memo != group.group_memo:
                discrepancies = (
                    f"group_memo: {existing_group.group_memo} -> {group.group_memo}"
                )
            if existing_group.group_create_time != datetime.fromtimestamp(
                group.group_create_time, tz=beijing_tz
            ):
                discrepancies = f"group_create_time: {existing_group.group_create_time} -> {datetime.fromtimestamp(group.group_create_time, tz=beijing_tz)}"
            if existing_group.member_count != group.member_count:
                discrepancies = f"member_count: {existing_group.member_count} -> {group.member_count}"
            if existing_group.max_member_count != group.max_member_count:
                discrepancies = f"max_member_count: {existing_group.max_member_count} -> {group.max_member_count}"

            print(
                f"记录 {group.group_id} {group.group_name} 存在，但数据不一致，准备更新。不一致的字段: {discrepancies}"
            )
            # 数据不一致，返回需要更新的标志
            return True
    else:
        # 记录不存在，返回需要插入的标志
        return True


async def query_qq_group_list(
    group_id: Optional[int] = None,
    group_name: Optional[str] = None,
    group_memo: Optional[str] = None,
    min_member_count: Optional[int] = None,
    max_member_count: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    order_by: Optional[str] = "-group_create_time",  # 默认按创建时间降序排序
) -> List[QQGroup]:
    # 创建基本的查询集
    query: QuerySet[QQGroup] = QQGroup.all()

    # 根据条件进行过滤
    if group_id is not None:
        query = query.filter(group_id=group_id)
    if group_name is not None:
        query = query.filter(group_name__icontains=group_name)
    if group_memo is not None:
        query = query.filter(group_memo__icontains=group_memo)
    if min_member_count is not None:
        query = query.filter(member_count__gte=min_member_count)
    if max_member_count is not None:
        query = query.filter(member_count__lte=max_member_count)
    if start_time is not None:
        query = query.filter(group_create_time__gte=start_time)
    if end_time is not None:
        query = query.filter(group_create_time__lte=end_time)

    # 排序功能
    query = query.order_by(order_by)

    # 分页
    query = query.offset(offset).limit(limit)

    # 返回结果
    return await query
