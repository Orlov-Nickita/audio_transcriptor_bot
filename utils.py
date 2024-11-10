import io
from typing import Generator
from openai import OpenAI
from loader import OPEN_AI_API_KEY


async def audio_to_text(io_file_bytes: io.BytesIO) -> str:
    """Принимает путь к аудио файлу, возвращает текст файла."""
    # return 'transcript.text'
    client = OpenAI(
        api_key=f"{OPEN_AI_API_KEY}",
        base_url="https://api.proxyapi.ru/openai/v1",
    )
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=io_file_bytes
    )
    return transcript.text


def chunked(iterable, chunk_size: int) -> Generator:
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i: i + chunk_size]
