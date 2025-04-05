import io

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import File
from loguru import logger

from balance import BalanceWorker, OpenAIModel
from utils import audio_to_text, chunked
from aiogram.types import Message

router: Router = Router()


class Auth(StatesGroup):
    not_authenticated = State()
    authenticated = State()
    audio = State()


@router.message(CommandStart())
async def send_welcome_func(message: Message) -> None:
    await message.reply(text='Добро пожаловать в транскрибатор аудио')


@router.message(Command(commands=['audio']))
async def transcript_audio(message: Message, state: FSMContext) -> None:
    await message.reply(text='Пришли аудио или введи "Отмена"')
    await state.set_state(Auth.audio)


@router.message(Command(commands=['balance']))
async def get_balance_for_transcript(message: Message) -> None:
    balance_worker = BalanceWorker()
    balance: OpenAIModel = await balance_worker.get_login()
    await message.reply(text=f'Ваш баланс: {balance.balance} рублей')


# @router.message(Auth.not_authenticated)
# async def process_message(message: Message):
#     await message.reply(text='Доступ закрыт')


# @router.message(F.content_type == "text")
# async def process_message_2(message: Message):
#     await message.reply(text='Привет, выбери команду!')


async def is_valid_file_format(message: Message, filename: str):
    valid_formats = ['flac', 'm4a', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']
    f_format = filename.split('.')[1]
    if f_format not in valid_formats:
        await message.reply(f'Недопустимый формат файла ({f_format}).\nРазрешено: {valid_formats}')
        return False
    return True


@router.message(Auth.audio, F.content_type == "document")
async def process_document_message(message: Message, bot: Bot, state: FSMContext):
    logger.debug(message.document)
    file_from_bot = await bot.get_file(message.document.file_id)
    await process_file(message, bot, state, file_from_bot)


@router.message(Auth.audio, F.content_type == "audio")
async def process_audio_message(message: Message, bot: Bot, state: FSMContext):
    logger.debug(message.audio)
    file_from_bot = await bot.get_file(message.audio.file_id)
    await process_file(message, bot, state, file_from_bot)


@router.message(Auth.audio, F.content_type == "voice")
async def process_voice_message(message: Message, bot: Bot, state: FSMContext):
    logger.debug(message.voice)
    file_from_bot = await bot.get_file(message.voice.file_id)
    await process_file(message, bot, state, file_from_bot)


@router.message(Auth.audio, F.content_type == "text")
async def cancel_upload(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.text == "Отмена" or message.text == "отмена":
        await bot.send_message(text="Загрузка отменена", chat_id=message.chat.id)
        await state.clear()


async def process_file(message: Message, bot: Bot, state: FSMContext, file_from_bot: File):
    logger.info(file_from_bot)
    tg_filename = file_from_bot.file_path.split('/')[1]
    logger.info(tg_filename)

    valid_format = await is_valid_file_format(message=message, filename=tg_filename)
    if valid_format:
        printing = await bot.send_message(
            chat_id=message.chat.id,
            text='Скачиваю файл...',
        )
        try:
            temp = await bot.download_file(file_path=file_from_bot.file_path, timeout=300)
            buffer = io.BytesIO(temp.read())
            buffer.name = tg_filename
            transcripting = await bot.send_message(
                chat_id=message.chat.id,
                text='Расшифровываю...',
            )
            transcripted_voice_text = await audio_to_text(io_file_bytes=buffer)
            await transcripting.delete()
        except Exception as error:
            await message.reply(f'{error}')
        else:
            if transcripted_voice_text:
                for chunk in chunked(transcripted_voice_text, chunk_size=4000):
                    await message.reply(text=chunk)
        finally:
            await printing.delete()
    await state.set_state(Auth.authenticated)
