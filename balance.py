from typing import Dict
import aiohttp
from pydantic import BaseModel

from loader import OPEN_AI_API_KEY


class OpenAIModel(BaseModel):
    balance: float


class BalanceWorker:
    async def _get_auth_data(self):
        return {
            "Authorization": f'Bearer {OPEN_AI_API_KEY}',
        }

    async def get_login(self) -> OpenAIModel:
        async with aiohttp.ClientSession() as session:
            headers = await self._get_auth_data()
            response = await session.get('https://api.aitunnel.ru/v1/aitunnel/balance', headers=headers)
            content: Dict = await response.json()
            return OpenAIModel(**content)
