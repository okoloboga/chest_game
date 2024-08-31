import logging

from aiogram_dialog import DialogManager
from aiogram.types import User
from fluentogram import TranslatorRunner
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import User as UserDataBase


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Getting info for subscribe of channel
async def start_getter(dialog_manager: DialogManager,
                       session: AsyncSession,
                       i18n: TranslatorRunner,
                       event_from_user: User,
                       **kwargs
                       ) -> dict:
    user_id = event_from_user.id 
    return {'start_dialog': i18n.start.dialog(),
            'button_subscribe': i18n.button.subscribe(),
            'button_check_subscribe': i18n.button.check.subscribe()}


