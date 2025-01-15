from tortoise import fields
from tortoise.models import Model


class QQSender(Model):
    id = fields.IntField(pk=True)  # 自动递增的主键
    user_id = fields.BigIntField(null=False)
    group_id = fields.BigIntField(null=False)  # 本地添加
    nickname = fields.CharField(max_length=255, null=False)
    card = fields.CharField(max_length=255, null=True)
    role = fields.CharField(max_length=50, null=False)
    title = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "qq_senders"
        unique_together = ("user_id", "group_id")  # 确保 user_id 和 group_id 的组合唯一
