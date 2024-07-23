import logging

from aiogram import Router
from aiogram.utils.deep_linking import decode_payload
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager 
from sqlalchemy.ext.asyncio.engine import AsyncEngine


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


# Select to Create new Game
async def create_game(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create new Game')


# Seacrh for 1 VS 1 Game
async def find_1vs1(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for 1VS1') 


# Search for SUPER Game
async def find_super(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for SUPER') 


# Create new 1 VS 1 Game
async def create_1vs1(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create 1VS1 Game') 


# Create new SUPER Game
async def create_super(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create SUPER Game')



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
async def find_deposit_0_5(callback: CallbackQuery,
                         button: Button,
                         dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for Deposit 0.5')


async def find_deposit_1(callback: CallbackQuery,
                         button: Button,
                         dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for Deposit 1')


async def find_deposit_2(callback: CallbackQuery,
                         button: Button,
                         dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for Deposit 2')


async def find_deposit_4(callback: CallbackQuery,
                         button: Button,
                         dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for Deposit 4')


async def find_deposit_8(callback: CallbackQuery,
                         button: Button,
                         dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for Deposit 8')
     

async def find_deposit_25(callback: CallbackQuery,
                          button: Button,
                          dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for Deposit 25')
    
    
async def find_deposit_50(callback: CallbackQuery,
                          button: Button,
                          dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for Deposit 50')


async def find_deposit_100(callback: CallbackQuery,
                           button: Button,
                           dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for Deposit 100')


# CREATE 
async def create_deposit_0_5(callback: CallbackQuery,
                           button: Button,
                           dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create Deposit 0.5')


async def create_deposit_1(callback: CallbackQuery,
                           button: Button,
                           dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create Deposit 1')


async def create_deposit_2(callback: CallbackQuery,
                           button: Button,
                           dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create Deposit 2')


async def create_deposit_4(callback: CallbackQuery,
                           button: Button,
                           dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create Deposit 4')


async def create_deposit_8(callback: CallbackQuery,
                           button: Button,
                           dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create Deposit 8')


async def create_deposit_25(callback: CallbackQuery,
                            button: Button,
                            dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create Deposit 25')
    

async def create_deposit_50(callback: CallbackQuery,
                            button: Button,
                            dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create Deposit 50')


async def create_deposit_100(callback: CallbackQuery,
                             button: Button,
                             dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create Deposit 100')
