import logging

from aiogram import Bot
from aiogram_dialog import DialogManager
from aiogram.types import User
from aiogram.utils.deep_linking import create_start_link
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import sessionmaker

from services import (coef_counter, game_result_writer,
                      get_user, CENTRAL_WALLET)


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Main menu getter
async def main_getter(dialog_manager: DialogManager,
                      i18n: TranslatorRunner,
                      bot: Bot,
                      event_from_user: User,
                      **kwargs
                      ) -> dict:
    # Is it after game?
    result = dialog_manager.start_data if dialog_manager.start_data is not None else None
    logger.info(f'Result is {result} - if it exit from game')
    user_id = event_from_user.id
    first_name = event_from_user.first_name
    logger.info(f'User {user_id} in Main Menu')
    
    return {'main_menu': i18n.welcome.dialog(name=first_name),
            'button_play': i18n.button.play(),
            'button_balance': i18n.button.balance(),
            'button_promocode': i18n.button.promocode(),
            'button_how_to_play': i18n.button.howtoplay(),
            'button_referrals': i18n.button.referrals(),
            'button_community': i18n.button.community()}
    

# Referral menu information
async def referrals_getter(dialog_manager: DialogManager,
                           i18n: TranslatorRunner,
                           bot: Bot,
                           event_from_user: User,
                           **kwargs
                           ) -> dict:
    
    user_id = event_from_user.id
    logger.info(f'User {user_id} in Referral Menu')
    session = dialog_manager.middleware_data.get('session')
    
    # getting user data from database for referrals count and coefs
    referrals_coef = await coef_counter(user_id, session)
    link = await create_start_link(bot, str(user_id), encode=True)
    
    return {'referrals': i18n.referrals(link=link,
                                        referrals=referrals_coef['referrals'],
                                        coef=referrals_coef['coef'],
                                        comission=int(referrals_coef['comission'] * 100)),
            'button_back': i18n.button.back()}
    
    
# Show TON balance of account and dirrect to import and export
async def ton_balance_getter(dialog_manager: DialogManager,
                             session: async_sessionmaker,
                             i18n: TranslatorRunner,
                             event_from_user: User,
                             **kwargs
                             ) -> dict:
    
    user_id = event_from_user.id
    logger.info(f'User {user_id} in TON Balace Menu')
    
    user = await get_user(session, user_id)
    logger.info(f'Ton balance getted for {user_id}: {user.ton}')
    
    return {'balance': i18n.balance(ton_balance=user.ton),
            'button_import': i18n.button.tonimport(),
            'button_export': i18n.button.tonexport(),
            'button_back': i18n.button.back()}
    
    
# Instruction for import TON to game balance
async def ton_import_getter(dialog_manager: DialogManager,
                            session: async_sessionmaker,
                            i18n: TranslatorRunner,
                            event_from_user: User,
                            **kwargs
                            ) -> dict:
    
    user_id = event_from_user.id
    logger.info(f'User {user_id} in TON Import Menu')
    
    return {'import': i18n.tonimport(id=user_id),
            'button_import_check': i18n.button.importcheck(),
            'button_get_wallet': i18n.button.getwallet(),
            'button_how_to_get_ton': i18n.button.howtogetton(),
            'button_back': i18n.button.back()}
    
    
# Instruction for export TON to game balance
async def ton_export_getter(dialog_manager: DialogManager,
                            session: async_sessionmaker,
                            i18n: TranslatorRunner,
                            event_from_user: User,
                            **kwargs
                            ) -> dict:
        
    user_id = event_from_user.id
    logger.info(f'User {user_id} in TON Export Menu')
    
    return {'export': i18n.tonexport(),
            'button_back': i18n.button.back()}
 

# Enter promocode
async def promocode_getter(dialog_manager: DialogManager,
                           session: async_sessionmaker,
                           i18n: TranslatorRunner,
                           event_from_user: User,
                           **kwargs
                           ) -> dict:

    user_id = event_from_user.id
    logger.info(f'User {user_id} in Enter Promocode menu')

    return {'enter_promocode': i18n.enter.promocode(),
            'button_back': i18n.button.back()}
