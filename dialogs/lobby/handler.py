import asyncio
import logging
import random

from aiogram import Router, Bot
from aiogram.types import CallbackQuery, Message, callback_query
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input.text import ManagedTextInput
from fluentogram import TranslatorRunner
from redis import asyncio as aioredis


from states import LobbySG, MainSG
from services import (create_room_query, get_game, get_user, message_delete,
                      write_as_guest)


lobby_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Select to Find Games
async def public_game(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Search for Game')
    dialog_manager.current_context().dialog_data['mode'] = 'public'

    await dialog_manager.switch_to(LobbySG.deposit)


# Select to Create new Game
async def private_game(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} Create new Game')
    dialog_manager.current_context().dialog_data['mode'] = 'private'

    await dialog_manager.switch_to(LobbySG.deposit)


# Go to plya Demo game vs BOT
async def demo_game(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} go to playe vs Bot in Demo game')
    dialog_manager.current_context().dialog_data['mode'] = 'demo'
    dialog_manager.current_context().dialog_data['deposit'] = 100

    await dialog_manager.switch_to(LobbySG.demo_ready)

''' 
       /$$/$$   /$$             
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


# Chose deposit
async def deposit(callback: CallbackQuery,
                  button: Button,
                  dialog_manager: DialogManager):
    
    user_id = callback.from_user.id
    deposit = (callback.data)[10:]
    deposit = 0.5 if deposit == '0_5' else int(deposit)
    session = dialog_manager.middleware_data.get('session')

    if (await get_user(session, user_id)).ton >= deposit:
        dialog_manager.current_context().dialog_data['deposit'] = deposit
        await dialog_manager.switch_to(LobbySG.game_confirm)
    else:
        i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
        bot: Bot = dialog_manager.middleware_data.get('bot')
        msg = await callback.message.answer(text=i18n.notenough.ton())
        await callback.answer()
        await asyncio.sleep(1)
        await dialog_manager.switch_to(LobbySG.deposit)
        await bot.delete_message(user_id, msg.message_id)
 

# Checking for existing game by invite code
async def join_private_game(message: Message,
                            widget: ManagedTextInput,
                            dialog_manager: DialogManager,
                            invite_code: str):
    
    user_id = message.from_user.id
    r = aioredis.Redis(host='localhost', port=6379)
    dialog_manager.current_context().dialog_data['mode'] = 'private'
    
    if await r.exists(invite_code) != 0:
        logger.info(f'User {user_id} join to {invite_code}')
        room = await r.hgetall(invite_code)
        deposit = float(str(room[b'deposit'], encoding='utf-8'))
        session = dialog_manager.middleware_data.get('session')

        if (await get_user(session, user_id)).ton >= deposit:
            dialog_manager.current_context().dialog_data['deposit'] = deposit
            dialog_manager.current_context().dialog_data['room'] = room
            await write_as_guest(room, user_id)
            await dialog_manager.switch_to(LobbySG.game_ready)
        else:
            i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
            bot: Bot = dialog_manager.middleware_data.get('bot')
            msg = await message.answer(text=i18n.notenough.ton())
            await asyncio.sleep(1)
            await dialog_manager.switch_to(LobbySG.deposit)
            await bot.delete_message(user_id, msg.message_id)
    else:
        logger.info(f'Game {invite_code} doesnt exists')
        i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
        await message.answer(text=i18n.game.notexists())
        await asyncio.sleep(1)
        await bot.delete_message(user_id, msg.message_id)


# Invited code is wrong completely
async def wrong_input(message: Message,
                      widget: ManagedTextInput,
                      dialog_manager: DialogManager,
                      invite_code: str):
    
    user_id = message.from_user.id
    logger.info(f'User {user_id} entered wrong invite_code')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    await message.answer(text=i18n.game.notexists())

    
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

    mode = dialog_manager.current_context().dialog_data['mode']
    
    if mode != 'private':
        is0 = random.randint(0, 5)
        logger.info(f'BOT CHECK: is0 = {is0}')
    else: 
        is0 = 1
        logger.info('Bot check is off')

    if is0 != 0:
        r = aioredis.Redis(host='localhost', port=6379)
        if mode == 'public':
            room = await r.hgetall('r_'+str(callback.from_user.id))
        else:
            room = await r.hgetall('pr_'+str(callback.from_user.id))
        logger.info(f'Current room status: {room}')
        
        if room[b'guest'] == b'wait':
            
            # Nothing new...
            i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
            await callback.message.edit_text(text=i18n.still.waiting.opponent())
            await asyncio.sleep(1)
        else:
            dialog_manager.current_context().dialog_data['room'] = room
            await dialog_manager.switch_to(LobbySG.game_ready)
    else:
        await dialog_manager.switch_to(LobbySG.demo_ready)


# Checking got game while searching
async def wait_check_search(callback: CallbackQuery,
                            button: Button,
                            dialog_manager: DialogManager):
    
    user_id = callback.from_user.id
    deposit = dialog_manager.current_context().dialog_data['deposit']
    result = await get_game(deposit)
    logger.info(f'Founded Game: {result}')

    if result == 'no_rooms':
        i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
        bot: Bot = dialog_manager.middleware_data.get('bot')
        msg = await callback.message.answer(text=i18n.still.searching.game())
        await asyncio.sleep(2)
        await bot.delete_message(user_id, msg.message_id)

    else:
        dialog_manager.current_context().dialog_data['room'] = result
        await write_as_guest(result, user_id)
        await dialog_manager.switch_to(LobbySG.game_ready)





