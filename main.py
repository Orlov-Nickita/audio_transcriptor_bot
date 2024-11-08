import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.methods import GetUpdates
from aiogram.types import BotCommand
from bot import router
from loader import BOT_TOKEN, redis_url


async def main():
    bot: Bot = Bot(token=BOT_TOKEN)
    bot.session.middleware(RequestLogging(ignore_methods=[GetUpdates]))

    commands = [
        BotCommand(command="/start", description="Начать"),
        BotCommand(command="/audio", description="Расшифровка"),
        BotCommand(command="/balance", description="Узнать баланс"),
    ]
    await bot.set_my_commands(commands)
    storage = RedisStorage.from_url(redis_url)
    dp: Dispatcher = Dispatcher(storage=storage)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print(1)
    asyncio.run(main())
