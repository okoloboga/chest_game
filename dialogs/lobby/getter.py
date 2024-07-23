import logging

from aiogram_dialog import DialogManager
from aiogram.types import User
from aiogram.utils.deep_linking import create_start_link
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import async_sessionmaker
from redis import asyncio as aioredis

from services import get_user


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Main menu of Lobby:
async def lobby_getter(dialog_manager: DialogManager,
                       session: async_sessionmaker,
                       i18n: TranslatorRunner,
                       bot: Bot,
                       event_from_user: User,
                       **kwargs
                       ) -> dict:
    
    user_id = event_from_user.id
    logger.info(f'User {user_id} in Lobby Menu')
    
    # Get TON value of user
    user_data = await get_user(session,
                               user_id)
    dialog_manager.current_context().dialog_data['ton'] = float(user_data.ton)
    
    return {'lobby_menu': i18n.lobby.menu(),
            'button_find_game': i18n.button.find.game(),
            'button_create_game': i18n.button.create.game(),
            'button_back': i18n.button.back()}
    
    
# Select type of game: Suber and 1VS1. For Create and Find
async def mode_getter(dialog_manager: DialogManager,
                      session: async_sessionmaker,
                      i18n: TranslatorRunner,
                      bot: Bot,
                      event_from_user: User,
                      **kwargs
                      ) -> dict:
    
    user_id = event_from_user.id
    logger.info(f'User {user_id} in Select Mode')
    
    return {'select_mode': i18n.select.mode(),
            'button_mode_1vs1': i18n.button.mode1vs1(),
            'button_mode_super': i18n.button.modesuper(),
            'button_back': i18n.button.back()}
    
    
# Select deposit for game. For Create and Find
async def deposit_getter(dialog_manager: DialogManager,
                         session: async_sessionmaker,
                         i18n: TranslatorRunner,
                         bot: Bot,
                         event_from_user: User,
                         **kwargs
                         ) -> dict:
    
    user_id = event_from_user.id
    logger.info(f'User {user_id} in Deposit Type')
    
    return {'select_deposit': i18n.select.deposit(),
            'button_back': i18n.button.back()}
    
    
# Not enough TON to make Deposit
async def not_enough_ton_getter(dialog_manager: DialogManager,
                                session: async_sessionmaker,
                                i18n: TranslatorRunner,
                                bot: Bot,
                                event_from_user: User,
                                **kwargs
                                ) -> dict:
    
    user_id = event_from_user.id
    logger.info(f'User {user_id} has not enough TON for Deposit')
    
    return {'not_enough_ton': i18n.notenough.ton(),
            'button_tonimport': i18n.button.tonimport(),
            'button_back': i18n.button.back()}
    
    
# Deposit made - waiting for Game!...
async def wait_game_getter(dialog_manager: DialogManager,
                           session: async_sessionmaker,
                           i18n: TranslatorRunner,
                           bot: Bot,
                           event_from_user: User,
                           **kwargs
                           ) -> dict:
    
    user_id = event_from_user.id
    find_create = dialog_manager.current_context().dialog_data['find_create']
    mode = dialog_manager.current_context().dialog_data['mode']
    deposit = dialog_manager.current_context().dialog_data['deposit']
    
    logger.info(f'User {user_id} {find_create} {mode} Game for {deposit} TON')
    
    r = aioredis.Redis(host='localhost', port=6379)
    
    
    return {'wait_game': i18n.wait.game(),
            'button_back': i18n.button.back()}