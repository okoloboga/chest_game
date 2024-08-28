import json
import logging

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

logger = logging.getLogger(__name__)
    
# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s'
)


class ShadowBanMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        with open('database/ban.json', 'r', encoding='utf-8') as ban_file:
            ban_list = (json.load(ban_file))['ban']
        logger.info(f'ban_list: {ban_list}')

        user: User = data.get('event_from_user')
        if user is not None:
            logger.info(f'User: {user.id}')
            if str(user.id) in ban_list:
                return

        return await handler(event, data)
