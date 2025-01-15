from tortoise import fields
from tortoise.models import Model


class QQMessage(Model):
    self_id = fields.BigIntField(null=False)
    user_id = fields.BigIntField(null=False)
    time = fields.DatetimeField(null=False)
    message_id = fields.BigIntField(pk=True)
    message_seq = fields.BigIntField(null=False)
    message_type = fields.CharField(max_length=50, null=False)
    sender = fields.ForeignKeyField("models.QQSender", related_name="messages")
    raw_message = fields.TextField(null=False)
    font = fields.IntField(null=False)
    sub_type = fields.CharField(max_length=50, null=False)
    message_format = fields.CharField(max_length=50, null=False)
    post_type = fields.CharField(max_length=50, null=False)
    group_id = fields.BigIntField(null=False)
    message = fields.JSONField(null=False)

    class Meta:
        table = "qq_messages"
