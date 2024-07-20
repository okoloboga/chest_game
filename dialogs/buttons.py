import logging

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from fluentogram import TranslatorRunner

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
    
    logger.info(f'User {callback.from_user.id} pressed to Back Button')
    
    await dialog_manager.start(state=MainSG.start,
                               mode=StartMode.RESET_STACK,
                               data={'user_id': callback.from_user.id}
                               )