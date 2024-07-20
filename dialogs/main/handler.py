import logging

from aiogram import Router
from aiogram.utils.deep_linking import decode_payload
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager

from sqlalchemy.ext.asyncio.engine import AsyncEngine


router_start = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Go to Lobby 
async def switch_to_lobby(callback: CallbackQuery,
                          bot: Bot,
                          dialog_manager: DialogManager):
    logger.info(f'User {callback.from_user.id} go to Lobby')
    await dialog_manager.start(LobbySG.main,
                               data={'user_id': callback.from_user.id})
    
    
# Go to balance page with import and export TON
async def balance(callback: CallbackQuery,
                  bot: Bot,
                  dialog_manager: DialogManager):
    logger.info(f'User {callback.from_user.id} go to Balance')
    await dialog_manager.switch_to(MainSG.ton_balance)


# Show Telegraph with Rules
async def how_to_play(callback: CallbackQuery,
                      bot: Bot,
                      dialog_manager: DialogManager):
    logger.info(f'User {callback.from_user.id} go to Telegraph page')


# Go to Referrals page: referral link, comission
async def referrals(callback: CallbackQuery,
                    bot: Bot,
                    dialog_manager: DialogManager):
    logger.info(f'User {callback.from_user.id} go to Referrals')
    await dialog_manager.switch_to(MainSG.referrals)


# Go to channel about Game
async def community(callback: CallbackQuery,
                    bot: Bot,
                    dialog_manager: DialogManager):
    logger.info(f'User {callback.from_user.id} go to Community Channel')
    pass


# Go to TON import page
async def ton_import(callback: CallbackQuery,
                     bot: Bot,
                     dialog_manager: DialogManager):
    logger.info(f'User {callback.from_user.id} go to TON import')
    await dialog_manager.switch_to(MainSG.ton_import)


# Go to TON export page
async def ton_export(callback: CallbackQuery,
                     bot: Bot,
                     dialog_manager: DialogManager):
    logger.info(f'User {callback.from_user.id} go to TON export')
    await dialog_manager.switch_to(MainSG.ton_export)


# Checking for succesfull import
async def import_check(callback: CallbackQuery,
                       bot: Bot,
                       dialog_manager: DialogManager):
    logger.info(f'User {callback.from_user.id} checking for import ...')


# Making export after filter pass
async def do_export(callback: CallbackQuery,
                    widget: ManagedTextInput,
                    dialog_manager: DialogManager,
                    result_list: str):
    logger.info(f'User {callback.from_user.id} doing export with validated data:')
    logger.info(f'{result_list}')


# Wrong export data filled
async def wrong_export(callback: CallbackQuery,
                       widget: ManagedTextInput,
                       dialog_manager: DialogManager,
                       result_list: str):

    logger.info(f'User {callback.from_user.id} fills wrong export data {result_list}')

    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    await callback.answer(text=i18n.wrong.export())