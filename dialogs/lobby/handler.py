import logging

from aiogram import Router
from aiogram.utils.deep_linking import decode_payload
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode

from states import LobbySG
from services import deposit

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

    await dialog_manager.switch_to(LobbySG.type)


# Select to Create new Game
async def create_game(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create new Game')
    dialog_manager.current_context().dialog_data['find_create'] = 'create'

    await dialog_manager.switch_to(LobbySG.mode)


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
    deposit = 0.5
    await deposit(user_id,
                  dialog_manager,
                  deposit)


async def deposit_1(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    deposit = 1
    await deposit(user_id,
                  dialog_manager,
                  deposit)


async def deposit_2(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    deposit = 2
    await deposit(user_id,
                  dialog_manager,
                  deposit)


async def deposit_4(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    deposit = 4
    await deposit(user_id,
                  dialog_manager,
                  deposit)
    

async def deposit_8(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    deposit = 8    
    await deposit(user_id,
                  dialog_manager,
                  deposit)
    

async def deposit_25(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):

    user_id = callback.from_user.id
    deposit = 25  
    await deposit(user_id,
                  dialog_manager,
                  deposit)   
    
    
async def deposit_50(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):

    user_id = callback.from_user.id
    deposit = 50
    await deposit(user_id,
                  dialog_manager,
                  deposit)
    

async def deposit_100(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):

    user_id = callback.from_user.id
    deposit = 100
    await deposit(user_id,
                  dialog_manager,
                  deposit)
    
    
# If Not Enough TON for Deposit...
async def import_from_lobby(callback: CallbackQuery,
                            button: Button,
                            dialog_manager: DialogManager):
    
    user_id = callback.from_user.id
    logger.info(f'User {user_id} Want to import TON')
    
    await dialog_manager.start(MainSG.ton_import,
                               mode=StartMode.RESET_STACK)