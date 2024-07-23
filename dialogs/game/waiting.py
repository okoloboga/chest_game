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
    
    logger.info(f'User {callback.from_user.id} enter the Game')

    await dialog_manager.reset_stack()
     
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
        
    msg = await callback.message.answer(text=i18n.wait.game())
    
    # Init Bot for delete last message
    bot_config = get_config(BotConfig, "bot")
    bot = Bot(token=bot_config.token.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    await bot.delete_message(callback.from_user.id, msg.message_id - 1)

    


