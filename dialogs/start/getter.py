import logging

from aiogram_dialog import DialogManager
from aiogram.types import User
from fluentogram import TranslatorRunner
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from database import User as UserDataBase
from services import create_user

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Getting info for subscribe of channel
async def start_getter(dialog_manager: DialogManager,
                       session: async_sessionmaker,
                       i18n: TranslatorRunner,
                       event_from_user: User,
                       **kwargs
                       ) -> dict:
    user_id = event_from_user.id 
    logger.info(f'User {user_id} starts dialog')

    return {'start_dialog': i18n.start.dialog(),
            'button_subscribe': i18n.button.subscribe(),
            'button_check_subscribe': i18n.button.check.subscribe()}


# Getting after checking of subscribtion
async def welcome_getter(dialog_manager: DialogManager,
                         i18n: TranslatorRunner,
                         event_from_user: User,
                         **kwargs
                         ) -> dict:

    user_id = event_from_user.id 

    logger.info(f'User {user_id} subscribed to channel')
    first_name = event_from_user.first_name
    dialog_manager.current_context().dialog_data['first_name'] = first_name
    payload = dialog_manager.start_data['payload']
    Sessionmaker: async_sessionmaker = dialog_manager.middleware_data.get('session')

    # Add new user to database as registred after subscribing
    await create_user(sessionmaker=Sessionmaker,
                      telegram_id=event_from_user.id,
                      first_name=event_from_user.first_name,
                      last_name=event_from_user.last_name)
    
    # Add referral to link Parent
    if payload is not None:
        user_stmt = select(UserDataBase).where(payload == UserDataBase.telegram_id)
        async with Sessionmaker() as session:
            parent_user = await session.execute(user_stmt)
            parent = parent_user.scalar()
            parent.referrals = parent.referrals + 1
            await session.commit()

    return {'welcome_dialog': i18n.welcome.dialog(name=first_name),
            'button_confirm': i18n.button.confirm()}
