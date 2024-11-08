import io
from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, File

from balance import BalanceWorker, OpenAILoginModel
from loader import ADMINISTRATORS
from utils import audio_to_text, chunked

router: Router = Router()


class Auth(StatesGroup):
    not_authenticated = State()
    authenticated = State()
    audio = State()


@router.message(CommandStart())
async def send_welcome_func(message: Message, state: FSMContext) -> None:
    if str(message.chat.id) in ADMINISTRATORS.values():
        await message.reply(text='Добро пожаловать в транскрибатор аудио')
        await state.set_state(Auth.authenticated)
    else:
        await message.reply(text='Доступ закрыт')
        await state.set_state(Auth.not_authenticated)


@router.message(Auth.authenticated, Command(commands=['audio']))
async def transcript_audio(message: Message, state: FSMContext) -> None:
    await message.reply(text='Пришли аудио')
    await state.set_state(Auth.audio)


@router.message(Auth.authenticated, Command(commands=['balance']))
async def get_balance_for_transcript(message: Message) -> None:
    balance_worker = BalanceWorker()
    balance: OpenAILoginModel = await balance_worker.get_login()
    await message.reply(text=f'Ваш баланс: {balance.user.balance} рублей')


@router.message(Auth.not_authenticated)
async def process_message(message: Message):
    await message.reply(text='Доступ закрыт')


@router.message(Auth.audio, F.content_type == "document")
async def process_document_message(message: Message, bot: Bot, state: FSMContext):
    get_file = await bot.get_file(message.document.file_id)
    await process_file(message, bot, state, get_file)


@router.message(Auth.audio, F.content_type == "audio")
async def process_audio_message(message: Message, bot: Bot, state: FSMContext):
    get_file = await bot.get_file(message.audio.file_id)
    await process_file(message, bot, state, get_file)


@router.message(Auth.audio, F.content_type == "voice")
async def process_voice_message(message: Message, bot: Bot, state: FSMContext):
    get_file = await bot.get_file(message.voice.file_id)
    await process_file(message, bot, state, get_file)


async def process_file(message: Message, bot: Bot, state: FSMContext, get_file: File):
    temp = await bot.download_file(file_path=get_file.file_path)
    buffer = io.BytesIO(temp.read())
    buffer.name = "file.mp3"
    try:
        transcripted_voice_text = await audio_to_text(buffer)
    except Exception as error:
        await message.reply(f'{error}')
    else:
        if transcripted_voice_text:
            for chunk in chunked(transcripted_voice_text, chunk_size=4000):
                await message.reply(text=chunk)
    await state.set_state(Auth.authenticated)
