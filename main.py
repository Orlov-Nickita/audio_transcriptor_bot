import asyncio
import os.path
from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.methods import GetUpdates
from aiogram.types import BotCommand, Message
from bot import router, Auth
from loader import BOT_TOKEN, redis_url, ADMINISTRATORS
from typing import Callable, Any, Awaitable, Dict
import logging
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        level = logger.level(record.levelname).name
        logger.log(level, record.getMessage())


class AuthMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if str(event.chat.id) in ADMINISTRATORS.values():
            await data['state'].set_state(Auth.authenticated)
            if data.get('command') and data['command'].text == '/audio':
                await data['state'].set_state(Auth.audio)
            return await handler(event, data)

        else:
            await event.reply(text='Доступ закрыт')
            await data['state'].set_state(Auth.not_authenticated)


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
    router.message.middleware(AuthMiddleware())

    dp: Dispatcher = Dispatcher(storage=storage)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    if not os.path.exists('logs'):
        os.makedirs('logs')
    print(1)
    logger.add("logs/logging_{time}.log", rotation="50 MB", level="DEBUG")
    logging.getLogger('aiogram').setLevel(logging.DEBUG)
    logging.getLogger('aiogram').addHandler(InterceptHandler())
    logging.getLogger('asyncio').setLevel(logging.DEBUG)
    logging.getLogger('asyncio').addHandler(InterceptHandler())

    asyncio.run(main())
