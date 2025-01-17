import logging

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from fluentogram import TranslatorRunner
from redis import asyncio as aioredis

from states import MainSG

router_buttons = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Process BACK button
async def back(callback: CallbackQuery,
               button: Button,
               dialog_manager: DialogManager):
    
    user_id = callback.from_user.id
    logger.info(f'User {callback.from_user.id} pressed to Back Button')
    r = aioredis.Redis(host='localhost', port=6379)
    try:
        if await r.exists('pr_' + str(user_id)):
            await r.delete('pr_' + str(user_id))
        elif await r.exists('r_' + str(user_id)):
            await r.delete('r_' + str(user_id))
    except TypeError:
        logger.info(f'User {user_id} havent created room')
    await dialog_manager.start(state=MainSG.main,
                               mode=StartMode.RESET_STACK)
