from tortoise import Tortoise

from app.config import STR_TZ_NAME


async def db_init():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={
            "models": [
                "app.models.QQgroup",
                "app.models.QQMessage",
                "app.models.QQSender",
            ]
        },
        use_tz=True,
        timezone=STR_TZ_NAME,
    )
    await Tortoise.generate_schemas()


async def db_close():
    await Tortoise.close_connections()
