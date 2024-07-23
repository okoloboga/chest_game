import logging

from aiogram_dialog import DialogManager
from aiogram.types import User
from aiogram.utils.deep_linking import create_start_link
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio.engine import AsyncEngine


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
    
    return {'lobby_menu': i18n.lobby.menu(),
            'button_find_game': i18n.button.find.game(),
            'button_create_game': i18n.button.create.game(),
            'button_back': i18n.button.back()}
    
    
# Select type of game: Suber and 1VS1. For Create and Find
async def type_getter(dialog_manager: DialogManager,
                      session: async_sessionmaker,
                      i18n: TranslatorRunner,
                      bot: Bot,
                      event_from_user: User,
                      **kwargs
                      ) -> dict:
    
    user_id = event_from_user.id
    logger.info(f'User {user_id} in Select Type')
    
    return {'select_type': i18n.select.type(),
            'button_find_1vs1': i18n.button.find1vs1(),
            'button_create_1vs1': i18n.button.create1vs1(),
            'button_find_super': i18n.button.find.super(),
            'button_create_super': i18n.button.create.super(),
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