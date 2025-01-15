from tortoise import fields
from tortoise.models import Model


class QQGroup(Model):
    group_id = fields.IntField(pk=True)
    group_name = fields.TextField(null=False)
    group_memo = fields.CharField(max_length=255, null=True)
    group_create_time = fields.DatetimeField(null=False)
    member_count = fields.IntField(null=False)
    max_member_count = fields.IntField(null=False)
