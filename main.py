import asyncio
import os
import os.path
from aiogram import Bot, Dispatcher
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.enums import ParseMode
from aiogram.filters import BaseFilter
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, Message
from bot import router
from loader import BOT_TOKEN, redis_url, ADMINISTRATORS
from typing import Any
import logging
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        level = logger.level(record.levelname).name
        logger.log(level, record.getMessage())


class AuthFilter(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message, **kwargs) -> Any:
        if str(message.chat.id) in ADMINISTRATORS.values():
            return True
        else:
            await message.reply(text='Доступ закрыт')

            await kwargs['bot'].send_message(
                chat_id=ADMINISTRATORS['Никита'],
                text="Попытка использовать бот:\n"
                     "tg_id: <code>{id}</code>\n"
                     "Ник: <code>{user}</code>\n"
                     "Имя: <code>{name}</code>\n"
                     "Фамилия: <code>{surname}</code>\n".format(
                    id=message.chat.id,
                    user=message.from_user.username,
                    name=message.from_user.first_name,
                    surname=message.from_user.last_name,
                ),
                parse_mode=ParseMode.HTML,
            )

            return False


async def main():
    bot: Bot = Bot(token=BOT_TOKEN)
    bot.session.middleware(RequestLogging())

    commands = [
        BotCommand(command="/start", description="Начать"),
        BotCommand(command="/audio", description="Расшифровка"),
        BotCommand(command="/balance", description="Узнать баланс"),
    ]
    await bot.set_my_commands(commands)
    # storage = RedisStorage.from_url(redis_url)
    router.message.filter(AuthFilter())
    dp: Dispatcher = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    if not os.path.exists('logs'):
        os.makedirs('logs')
    print('started')
    logger.add("logs/logging_{time}.log", rotation="50 MB", level="DEBUG")
    # logging.getLogger('aiogram').setLevel(logging.DEBUG)
    # logging.getLogger('aiogram').addHandler(InterceptHandler())
    # logging.getLogger('asyncio').setLevel(logging.DEBUG)
    # logging.getLogger('asyncio').addHandler(InterceptHandler())

    asyncio.run(main())
