import logging

from aiogram import Router
from aiogram.types import CallbackQuery, callback_query
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from fluentogram import TranslatorRunner
from redis import asyncio as aioredis

from states import LobbySG, MainSG
from services import (create_room_query, get_game, 
                      write_as_guest)

lobby_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Select to Find Games
async def find_game(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for Game')
    dialog_manager.current_context().dialog_data['mode'] = 'public'

    await dialog_manager.switch_to(LobbySG.deposit)


# Select to Create new Game
async def create_game(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create new Game')
    dialog_manager.current_context().dialog_data['mode'] = 'private'

    await dialog_manager.switch_to(LobbySG.deposit)

''' 
       /$$                                         /$$   /$$             
      | $$                                        |__/  | $$             
  /$$$$$$$  /$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$$ /$$ /$$$$$$ 
 /$$__  $$ /$$__  $$ /$$__  $$ /$$__  $$ /$$_____/| $$|_  $$_/
| $$  | $$| $$$$$$$$| $$  \ $$| $$  \ $$|  $$$$$$ | $$  | $$   
| $$  | $$| $$_____/| $$  | $$| $$  | $$ \____  $$| $$  | $$ /$$
|  $$$$$$$|  $$$$$$$| $$$$$$$/|  $$$$$$/ /$$$$$$$/| $$  |  $$$$/
 \_______/ \_______/| $$____/  \______/ |_______/ |__/   \___/ 
                    | $$                                                 
                    | $$                                                 
                    |__/  
'''

# FIND 
async def deposit(callback: CallbackQuery,
                  button: Button,
                  dialog_manager: DialogManager):
    
    deposit = (callback.data)[10:]
    deposit = 0.5 if deposit == '0_5' else int(deposit)

    dialog_manager.current_context().dialog_data['deposit'] = deposit
    await dialog_manager.switch_to(LobbySG.game_confirm)

    
# If Not Enough TON for Deposit...
async def import_from_lobby(callback: CallbackQuery,
                            button: Button,
                            dialog_manager: DialogManager):
    
    user_id = callback.from_user.id
    logger.info(f'User {user_id} Want to import TON')
    
    await dialog_manager.start(MainSG.ton_import,
                               mode=StartMode.RESET_STACK)
    
# CONFIRM GAME FINALLY
async def confirm_game(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager):

    user_id = callback.from_user.id
    await create_room_query(user_id, dialog_manager)
  
'''
                         /$$   /$$    
                        |__/  | $$    
 /$$  /$$  /$$  /$$$$$$  /$$ /$$$$$$  
| $$ | $$ | $$ |____  $$| $$|_  $$_/  
| $$ | $$ | $$  /$$$$$$$| $$  | $$    
| $$ | $$ | $$ /$$__  $$| $$  | $$ /$$
|  $$$$$/$$$$/|  $$$$$$$| $$  |  $$$$/
 \_____/\___/  \_______/|__/   \___/ 
'''


# Checking for founded guest in 1VS1
async def wait_check_o(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager):
    
    r = aioredis.Redis(host='localhost', port=6379)
    room = await r.hgetall('r_'+str(callback.from_user.id))
    logger.info(f'Current room status: {room}')
    
    if room[b'guest'] == b'wait':
        
        # Nothing new...
        i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
        await callback.message.answer(text=i18n.still.waiting.opponent())
    else:
        dialog_manager.current_context().dialog_data['room'] = room
        await dialog_manager.switch_to(LobbySG.game_ready)


# Checking got game while searching
async def wait_check_search(callback: CallbackQuery,
                            button: Button,
                            dialog_manager: DialogManager):
    
    deposit = dialog_manager.current_context().dialog_data['deposit']
    
    result = await get_game(deposit)
    logger.info(f'Founded Game: {result}')

    if result == 'no_rooms':
        i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
        await callback.message.answer(text=i18n.still.searching.game())
    else:
        dialog_manager.current_context().dialog_data['room'] = result
        await write_as_guest(result, callback.from_user.id)
        await dialog_manager.switch_to(LobbySG.game_ready)

