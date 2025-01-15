from typing import TypeVar, Generic, List
from pydantic import BaseModel


class QQGroupInfo(BaseModel):
    group_id: int
    group_name: str
    group_memo: str
    group_create_time: int
    member_count: int
    max_member_count: int


class QQSender(BaseModel):
    user_id: int
    nickname: str
    card: str
    role: str
    title: str


class QQMessage(BaseModel):
    self_id: int
    user_id: int
    time: int
    message_id: int
    message_seq: int
    message_type: str
    sender: QQSender
    raw_message: str
    font: int
    sub_type: str
    message_format: str
    post_type: str
    group_id: int
    message: List[dict]


T = TypeVar("T")


class QQResponse(BaseModel, Generic[T]):
    status: str
    retcode: int
    data: List[T]


class QQResponseData(BaseModel, Generic[T]):
    messages: List[T]


class QQResponseCustom(BaseModel, Generic[T]):
    status: str
    retcode: int
    data: QQResponseData[T]


QQGroupResponse = QQResponse[QQGroupInfo]
QQMessageResponse = QQResponseCustom[QQMessage]
