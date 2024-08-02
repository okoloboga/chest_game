import logging

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager 
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input.text import ManagedTextInput
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from services import (import_ton_check, process_transaction, 
                      export_ton, decrement_ton, get_user)
from services.constants import CENTRAL_WALLET
from states import MainSG, LobbySG
from database import User

main_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Go to Lobby 
async def switch_to_lobby(callback: CallbackQuery,
                          button: Button,
                          dialog_manager: DialogManager):
    
    logger.info(f'User {callback.from_user.id} go to Lobby')
    await dialog_manager.start(LobbySG.main,
                               data={'user_id': callback.from_user.id})
    
    
# Go to balance page with import and export TON
async def balance(callback: CallbackQuery,
                  button: Button,
                  dialog_manager: DialogManager):
    
    logger.info(f'User {callback.from_user.id} go to Balance')
    await dialog_manager.switch_to(MainSG.ton_balance)


# Go to Referrals page: referral link, comission
async def referrals(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):
    
    logger.info(f'User {callback.from_user.id} go to Referrals')
    await dialog_manager.switch_to(MainSG.referrals)


# Go to TON import page
async def ton_import(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):
    
    logger.info(f'User {callback.from_user.id} go to TON import')
    await dialog_manager.switch_to(MainSG.ton_import)


# Go to TON export page
async def ton_export(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):
    
    logger.info(f'User {callback.from_user.id} go to TON export')
    await dialog_manager.switch_to(MainSG.ton_export)


# Get Central Wallet address for import TON
async def get_wallet(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):
    
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    await callback.message.answer(text=i18n.central.wallet(wallet=CENTRAL_WALLET))


# Checking for succesfull import
async def import_check(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager):
    
    user_id = callback.from_user.id 
    logger.info(f'User {user_id} checking for import ...')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')

    result = await import_ton_check(user_id)
     
    if type(result) is dict:
    
        session: AsyncSession = dialog_manager.middleware_data.get('session')

        # Checking for used transactions
        transaction_hash = result['hash']
        transaction_value = result['value']
        
        transaction_check = await process_transaction(session,
                                                      user_id,
                                                      transaction_hash,
                                                      transaction_value)
        if transaction_check:
            await callback.answer(text=i18n.tonimport.success(value=result['value']))
        else:
            # Transaction is old - send notification
            await callback.answer(text=i18n.old.transaction(t_hash=transaction_hash,
                                                            t_value=transaction_value))
            
    elif result == 'not_unough':
        await callback.answer(text=i18n.notenough.transaction())
        
    elif result == 'no_transaction':
        await callback.answer(text=i18n.no.transaction())


# Making export after filter pass
async def do_export(callback: CallbackQuery,
                    widget: ManagedTextInput,
                    dialog_manager: DialogManager,
                    result_list: list):
    
    user_id = callback.from_user.id
    logger.info(f'User {user_id} doing export with validated data:')
    logger.info(f'{result_list}')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    session = dialog_manager.middleware_data['session']   
    
    user_balance = (await get_user(session, user_id)).ton

    logger.info(f'Users {user_id} balance is {user_balance}')

    if float(user_balance) > float(result_list[1]):
        result = await export_ton(user_id=user_id,
                                  amount=float(result_list[1]),
                                  destination_address=result_list[0])        
        if result:    
            result_decrement = await decrement_ton(session, user_id, result_list[1])
            
            # If users TON is enough...
            if result_decrement is True:
                await callback.answer(text=i18n.tonexport.success(value=result_list[1],
                                                                  address=result_list[0]))
            else:
                await callback.answer(text=i18n.tonexport.notenough(value=result_list[1],
                                                                    user_ton=user_balance))
        # If no transaction in exports...
        else:
            await callback.answer(text=i18n.tonexport.error())
    else:
        await callback.answer(text=i18n.tonexport.notenough(value=result_list[1],
                                                            user_ton=result_decrement))
 


# Wrong export data filled
async def wrong_export(callback: CallbackQuery,
                       widget: ManagedTextInput,
                       dialog_manager: DialogManager,
                       result_list: str):

    logger.info(f'User {callback.from_user.id} fills wrong export data {result_list}')

    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    await callback.answer(text=i18n.wrong.export())
