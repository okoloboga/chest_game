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


admin_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


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


# Processing edit promocodes
async def complete_edit_promocode(message: Message,
                                  widget: ManagedTextInput,
                                  dialog_manager: DialogManager,
                                  promocode: str):

    pass


# Processing ban/unban players
async def complete_ban_player(message: Message,
                              widget: ManagedTextInput,
                              dialog_manager: DialogManager,
                              ban: str):

    pass


# Processing sending messages to all players
async def complete_send_messages(message: Message,
                                 widget: ManagedTextInput,
                                 dialog_manager: DialogManager,
                                 messages: str):

    pass
