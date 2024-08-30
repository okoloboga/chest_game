import asyncio
import logging
import random

from aiogram import Router, Bot
from aiogram.types import CallbackQuery, Message, callback_query
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input.text import ManagedTextInput
from fluentogram import TranslatorRunner
from redis import asyncio as aioredis

from states import AdminSG
from services import (edit_promocode_process, ban_player_process, get_users_id,
                      admin_panel_info, write_off_function)


admin_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Go back to main admin
async def back_admin(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):

    await dialog_manager.switch_to(AdminSG.main)


# Go to Sending Message window
async def send_messages(callback: CallbackQuery,
                        button: Button,
                        dialog_manager: DialogManager):

    await dialog_manager.switch_to(AdminSG.send_messages)


# Go to Edit promocode window
async def edit_promocode(callback: CallbackQuery,
                         button: Button,
                         dialog_manager: DialogManager):

    await dialog_manager.switch_to(AdminSG.edit_promocode)


# Go to Ban/Unban Window
async def ban_player(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):

    await dialog_manager.switch_to(AdminSG.ban_player)


async def write_off(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    await dialog_manager.switch_to(AdminSG.write_off)


# Processing writing off
async def write_off_process(message: Message,
                            widget: ManagedTextInput,
                            dialog_manager: DialogManager,
                            write_off: float):
    
    user_id = message.from_user.id
    session = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    pure_income = (await admin_panel_info(session))['pure_income']

    if pure_income >= write_off:
        await write_off_function(session, write_off)
        logger.info('Writing off complete')
        msg = await message.answer(text=i18n.write.off.complete())
    else:
        logger.info('Writing off ERROR')
        msg = await message.answer(text=i18n.write.off.notenough())

    await asyncio.sleep(2)
    await bot.delete_message(user_id, msg.message_id)


# Processing edit promocodes
async def complete_edit_promocode(message: Message,
                                  widget: ManagedTextInput,
                                  dialog_manager: DialogManager,
                                  promocode: str):
    user_id = message.from_user.id
    session = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    result = await edit_promocode_process(session, promocode)
    
    logger.info(f'complete_edit_promocode({promocode})')

    if result == 'added':
        msg = await message.answer(text=i18n.promocode.added())
    elif result == 'removed':
        msg = await message.answer(text=i18n.promocode.removed())
    elif result == 'no_promocode':
        msg = await message.answer(text=i18n.nopromocode())
    elif result == 'invalid_command':
        msg = await message.answer(text=i18n.invalid.command())
    
    await asyncio.sleep(2)
    await bot.delete_message(user_id, msg.message_id)


# Processing ban/unban players
async def complete_ban_player(message: Message,
                              widget: ManagedTextInput,
                              dialog_manager: DialogManager,
                              ban: str):

    user_id = message.from_user.id
    bot: Bot = dialog_manager.middleware_data.get('bot')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    result = ban_player_process(ban)

    logger.info(f'complete_ban_player({ban})')
    
    if result == 'banned':
        msg = await message.answer(text=i18n.user.banned())
    elif result == 'banned_yet':
        msg = await message.answer(text=i18n.user.banned.yet())
    elif result == 'unbanned':
        msg = await message.answer(text=i18n.user.unbanned())
    elif result == 'notbanned':
        msg = await message.answer(text=i18n.user.notbanned())
    elif result == 'invalid_command':
        msg = await message.answer(text=i18n.invalid.command())
    
    await asyncio.sleep(2)
    await bot.delete_message(user_id, msg.message_id)


# Processing sending messages to all players
async def complete_send_messages(message: Message,
                                 widget: ManagedTextInput,
                                 dialog_manager: DialogManager,
                                 messages: str):

    user_id = message.from_user.id
    session = dialog_manager.middleware_data.get('session')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    
    result = await get_users_id(session)

    for id in result:
        await bot.send_message(id, messages)
    msg = await message.answer(text=i18n.all.messages.sended())
    await asyncio.sleep(2)
    await bot.delete_message(user_id, msg.message_id)
