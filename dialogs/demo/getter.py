import logging
import asyncio

from aiogram import Bot
from aiogram_dialog import DialogManager
from aiogram.types import User
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import async_sessionmaker
from redis import asyncio as aioredis
from base64 import b64encode

from services import get_user, bot_thinking


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Demo Main - confirm Ready for Game
async def demo_game_ready_getter(dialog_manager: DialogManager,
                                 session: async_sessionmaker,
                                 i18n: TranslatorRunner,
                                 event_from_user: User,
                                 **kwargs) -> dict:

    user_id = event_from_user.id
    deposit = dialog_manager.current_context().dialog_data['deposit']

    if deposit is None:
        deposit = 100
 
    logger.info(f'User {user_id} in Demo Game Ready, with Deposit: {deposit}')

    return {'demo_game_ready': i18n.game.ready(deposit=deposit),
            'button_demo_game_ready': i18n.button.game.ready(),
            'button_back': i18n.back()}


# Demo - Hidder is hidding treasure
async def demo_hidder_active_getter(dialog_manager: DialogManager,
                                    session: async_sessionmaker,
                                    i18n: TranslatorRunner,
                                    event_from_user: User,
                                    **kwargs) -> dict:

    user_id = event_from_user.id
    logger.info(f'User {user_id} hiding his treasure!')

    return {'demo_hidder_active': i18n.game.hidder(),
            'button_chest_1': i18n.button.chest.first(),
            'button_chest_2': i18n.button.chest.second(),
            'button_chest_3': i18n.button.chest.third(),
            'button_demo_exit': i18n.button.exit()}


# Demo - Hidder waiting for result
async def demo_hidder_wait_getter(dialog_manager: DialogManager,
                                  session: async_sessionmaker,
                                  i18n: TranslatorRunner,
                                  event_from_user: User,
                                  **kwargs) -> dict:

    user_id = event_from_user.id
    logger.info(f'User {user_id} waiting for Searcher')
    await asyncio.create_task(bot_thinking(dialog_manager,
                                           user_id), 
                              name=f'b_{user_id}')

    return {'demo_hidder_wait': i18n.game.hidden(),
            'button_demo_exit': i18n.button.exit}


# Demo - Searcher is searching treasure
async def demo_searcher_active_getter(dialog_manager: DialogManager,
                                      session: async_sessionmaker,
                                      i18n: TranslatorRunner,
                                      event_from_user: User,
                                      **kwargs) -> dict:

    user_id = event_from_user.id
    logger.info(f'User {user_id} searching treasure!')

    return {'demo_searcher_active': i18n.game.hidder(),
            'button_chest_1': i18n.button.chest.first(),
            'button_chest_2': i18n.button.chest.second(),
            'button_chest_3': i18n.button.chest.third(),
            'button_demo_exit': i18n.button.exit()}


# Demo - Searcher waiting for Hidder
async def demo_searcher_wait_getter(dialog_manager: DialogManager,
                                    session: async_sessionmaker,
                                    i18n: TranslatorRunner,
                                    event_from_user: User,
                                    **kwargs) -> dict:

    user_id = event_from_user.id
    logger.info(f'User {user_id} waiting for Hidder')
    await asyncio.create_task(bot_thinking(dialog_manager, 
                                           user_id), 
                              name=f'b_{user_id}')
    
    return {'demo_searcher_wait': i18n.game.wait.searcher(),
            'button_demo_exit': i18n.button.exit}


# Demo - Results of game
async def demo_game_end_getter(dialog_manager: DialogManager,
                               session: async_sessionmaker,
                               i18n: TranslatorRunner,
                               event_from_user: User,
                               **kwargs) -> dict:

    user_id = event_from_user.id
    logger.info(f'User {user_id} ended Demo Game')
    result = dialog_manager.current_context().dialog_data['result']

    if result == 'win':
        answer = i18n.game.youwin()
    elif result == 'lose':
        answer = i18n.game.youlose()

    return {'demo_game_result': answer,
            'button_demo_end': i18n.button.game.end()}

