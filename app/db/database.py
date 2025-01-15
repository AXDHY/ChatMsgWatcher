from tortoise import Tortoise


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
    )
    await Tortoise.generate_schemas()


async def db_close():
    await Tortoise.close_connections()
