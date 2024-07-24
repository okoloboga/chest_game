import logging
import pprint

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from fluentogram import TranslatorRunner
from redis import asyncio as aioredis

from states import GameSG, LobbySG
from config import get_config, BotConfig
from services import get_game


waiting_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Created Room or Query - now un GameSG, without Dialog
@waiting_router.callback_query(StateFilter(LobbySG.game_confirm))
async def confirm_game(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager
                       ):
    
    pass
    
    

