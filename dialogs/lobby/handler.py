import logging

from aiogram import Router
from aiogram.types import CallbackQuery
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
    dialog_manager.current_context().dialog_data['find_create'] = 'find'
    dialog_manager.current_context().dialog_data['mode'] = '1vs1'

    # await dialog_manager.switch_to(LobbySG.mode)
    await dialog_manager.switch_to(LobbySG.deposit)


# Select to Create new Game
async def create_game(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create new Game')
    dialog_manager.current_context().dialog_data['find_create'] = 'create'
    dialog_manager.current_context().dialog_data['mode'] = '1vs1'

    # await dialog_manager.switch_to(LobbySG.mode)
    await dialog_manager.switch_to(LobbySG.deposit)


'''
# Seacrh or create for 1 VS 1 Game
async def mode_1vs1(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} mode is 1VS1') 
    dialog_manager.current_context().dialog_data['mode'] = '1vs1'

    await dialog_manager.switch_to(LobbySG.deposit)


# Search or create for SUPER Game
async def mode_super(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} mode is SUPER') 
    dialog_manager.current_context().dialog_data['mode'] = 'super'

    await dialog_manager.switch_to(LobbySG.deposit)
'''   


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
async def deposit_0_5(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):

    user_id = callback.from_user.id
    dialog_manager.current_context().dialog_data['deposit'] = 0.5
    await dialog_manager.switch_to(LobbySG.game_confirm)


async def deposit_1(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    dialog_manager.current_context().dialog_data['deposit'] = 1
    await dialog_manager.switch_to(LobbySG.game_confirm)


async def deposit_2(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    dialog_manager.current_context().dialog_data['deposit'] = 2
    await dialog_manager.switch_to(LobbySG.game_confirm)


async def deposit_4(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    dialog_manager.current_context().dialog_data['deposit'] = 4
    await dialog_manager.switch_to(LobbySG.game_confirm)
    

async def deposit_8(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    dialog_manager.current_context().dialog_data['deposit'] = 8
    await dialog_manager.switch_to(LobbySG.game_confirm)
    

async def deposit_25(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):

    user_id = callback.from_user.id
    dialog_manager.current_context().dialog_data['deposit'] = 25
    await dialog_manager.switch_to(LobbySG.game_confirm) 
    
    
async def deposit_50(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):

    user_id = callback.from_user.id
    dialog_manager.current_context().dialog_data['deposit'] = 50
    await dialog_manager.switch_to(LobbySG.game_confirm)
    

async def deposit_100(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):

    user_id = callback.from_user.id
    dialog_manager.current_context().dialog_data['deposit'] = 100
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
    await create_room_query(user_id,
                            dialog_manager)
  
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
    room = await r.hgetall('ro_'+str(callback.from_user.id))
    logger.info(f'Current room status: {room}')
    
    if room[b'guest'] == b'wait':
        
        # Nothing new... 
        await callback.message.answer(text=i18n.still.waiting.opponent())
    else:
        await dialog_manager.switch_to(LobbySG.game_ready)


# Checking for founded guests in SUPER
'''
async def wait_check_s(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager):
    pass


# Owner of game room is Ready
async def owner_ready(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):
    pass
'''


# Checking got game while searching
async def wait_check_search(callback: CallbackQuery,
                            button: Button,
                            dialog_manager: DialogManager):
    
    mode = dialog_manager.current_context().dialog_data['mode']
    deposit = dialog_manager.current_context().dialog_data['deposit']
    
    query = {'mode': mode,
             'deposit': deposit}
    
    result = await get_game(query)
    if result == 'no_rooms':
        i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
        await callback.message.answer(text=i18n.still.searching.game())
    else:
        await write_as_guest(result, callback.from_user.id)
        await dialog_manager.switch_to(LobbySG.game_ready(),
                                       data={'room': result})
        
'''
# Checking for ready of another players in SUPER Mode
async def joined_check_s(callback: CallbackQuery,
                         button: Button,
                         dialog_manager: DialogManager):
    pass


# Ready for SUPER game
async def joined_ready(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager):
    pass
'''

