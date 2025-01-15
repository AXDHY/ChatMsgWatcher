from typing import List
from pydantic import BaseModel


class QQGroupInfo(BaseModel):
    group_id: int
    group_name: str
    group_memo: str
    group_create_time: int
    member_count: int
    max_member_count: int


class QQGroupResponse(BaseModel):
    status: str
    retcode: int
    data: List[QQGroupInfo]
