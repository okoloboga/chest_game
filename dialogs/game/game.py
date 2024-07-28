import logging
import pprint

from aiogram import F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager

from fluentogram import TranslatorRunner
from redis import asyncio as aioredis

from states import GameSG, LobbySG
from config import get_config, BotConfig
from services import get_game, room_to_game
from .keyboard import *

game_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Created Room or Query - now un GameSG, without Dialog
# Returning Game menu for HIdder or Searcher 
# And delete last message
@game_router.callback_query(StateFilter(LobbySG.game_confirm))
async def confirm_game(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager
                       ):
    
    user_id = callback.from_user.id
    result = await room_to_game(user_id)
    r = aioredis.Redis(host='localhost', port=6379)
    logger.info(f'User {callback.from_user.id} start game: {result}')
    
    await dialog_manager.reset_stack()

    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    
    # Getting hidder from Game data
    user_game_str = await r.get(user_id)
    user_game = await r.hgetall('go_'+str(user_game_str, encoding='utf-8'))
    hidder = str(user_game[b'hidder'], encoding='utf-8')

    # Checking users Role in that game
    if hidder == user_id:
        msg = await callback.message.answer(text=i18n.menu.hidder(),
                                            reply_markup=hidder_keyboard(i18n))
    else:
        msg = await callback.message.answer(text=i18n.menu.searcher(),
                                            reply_markup=searcher_wait_keyboard(i18n))

    # Init bot
    bot_config = get_config(BotConfig, 'bot')
    bot = Bot(token=bot_config.token.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await bot.delete_message(user_id, msg.message_id - 1)
