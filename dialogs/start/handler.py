import logging

from aiogram import Router, Bot
from aiogram.utils.deep_linking import decode_payload
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from states import MainSG, StartSG
from services import create_user, get_user, DOG_CHANNEL, add_referral


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
    session: AsyncSession = dialog_manager.middleware_data.get('session')
    logger.info(f'Referral data: {command}')

    # If user start bot by referral link 
    if command.args:
        logger.info(f'CommandObject is {command}')
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
        await dialog_manager.start(MainSG.main)


# Checking for channel subscribe
async def check_subscribe(callback: CallbackQuery,
                          button: Button,
                          dialog_manager: DialogManager):

    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    bot: Bot = dialog_manager.middleware_data.get('bot')

    user_channel_status = await bot.get_chat_member(chat_id=DOG_CHANNEL, 
                                                    user_id=callback.from_user.id)

    if user_channel_status.status != 'left':

        session: AsyncSession = dialog_manager.middleware_data.get('session')
        payload = dialog_manager.start_data['payload']

        # Add new User to Database
        await create_user(session,
                          callback.from_user.id,
                          callback.from_user.first_name,
                          callback.from_user.last_name)
        logger.info(f'Payload before adding referral: {payload}')

        # Add referral to link Parent
        if payload is not None:
            await add_referral(session, payload, callback.from_user.id)

        await dialog_manager.switch_to(StartSG.welcome)
    else:
        await callback.answer(text=i18n.need.subscribe())


# Confirming registration after subscribing to channel
async def start_confirm(callback: CallbackQuery,
                        button: Button,
                        dialog_manager: DialogManager):
    
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')

    await dialog_manager.start(MainSG.main)

