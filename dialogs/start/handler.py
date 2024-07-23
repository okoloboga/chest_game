import logging

from aiogram import Router, Bot
from aiogram.utils.deep_linking import decode_payload
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager

from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from states import StartSG
from services import create_user, get_user
from .services import CHANNEL


start_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Process START CommandStart
@start_router.message(CommandStart(deep_link_encoded=True))
async def command_start_getter(message: Message,
                               dialog_manager: DialogManager,
                               command: CommandObject):

    user_id = message.from_user.id
    session = dialog_manager.middleware_data['session']

    # If user start bot by referral link 
    if command.args:
        lgger.info(f'CommandObject is {command}')
        args = command.args
        payload = decode_payload(args)
    else:
        payload = None

    user = await get_user(session, user_id)
    logger.info(f'User from database {user}')

    # If user new - give him to subscribe
    if user is None:
        await dialog_manager.start(StartSG.start,
                                   data={'user_id': user_id,
                                         'payload': payload})
    else:
        await dialog_manager.start(MainSG.start,
                                   data={'user_id': user_id})



# Checking for channel subscribe
async def check_subscribe(callback: CallbackQuery,
                          bot: Bot,
                          dialog_manager: DialogManager):
    i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']

    user_channel_status = await bot.get_chat_member(chat_id=CHANNEL, user_id=callback.from_user.id)

    if user_channel_status.status != 'left':
        await dialog_manager.switch_to(StartSG.welcome)
    else:
        await callback.answer(text=i18n.need.subscribe())


# Confirming registration after subscribing to channel
async def start_confirm(callback: CallbackQuery,
                        bot: Bot,
                        dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start,
                               data={'user_id': callback.from_user.id})


