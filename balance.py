import asyncio
import datetime
from typing import Dict
import aiohttp
from pydantic import BaseModel

from loader import OPEN_AI_LOGIN, OPEN_AI_PASS


class OpenAIUserModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    is_active: bool
    balance: float
    api_keys_limit: int
    created_at: datetime.datetime


class OpenAILoginModel(BaseModel):
    token: str
    refresh_token: str
    user: OpenAIUserModel


class BalanceWorker:
    def __init__(self):
        self.login = OPEN_AI_LOGIN
        self.password = OPEN_AI_PASS

    async def _get_auth_data(self):
        return {
            'email': self.login,
            'password': self.password,
        }

    async def get_login(self) -> OpenAILoginModel:
        async with aiohttp.ClientSession() as session:
            headers = await self._get_auth_data()
            response = await session.post('https://local.proxyapi.ru/auth/login', json=headers)
            content: Dict = await response.json()
            return OpenAILoginModel(**content)
