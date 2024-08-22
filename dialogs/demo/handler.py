import logging
import random
import asyncio

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from states import DemoSG
from services import demo_result_writer, bot_thinking


demo_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Confirm Demo game start
async def game_demo_start(callback: CallbackQuery,
                          button: Button,
                          dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} confirmed Demo game')
    role = random.choice(['hidder', 'searcher'])
    
    # Checking for Demo game, or Public
    try:
        mode = dialog_manager.start_data['demo']
        dialog_manager.current_context().dialog_data['mode'] = mode
    except KeyError:
        dialog_manager.current_context().dialog_data['mode'] = 'public'
        
    dialog_manager.current_context().dialog_data['role'] = role

    if role == 'hidder':
        await dialog_manager.switch_to(DemoSG.hidder_active)
    elif role == 'searcher':
        await dialog_manager.switch_to((DemoSG.searcher_wait))
        await asyncio.create_task(bot_thinking(dialog_manager, user_id))
    

# Process Selecting Chest
async def select_chest(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} selected the Chest')
    role = dialog_manager.current_context().dialog_data['role']

    if role == 'hidder':
        await dialog_manager.switch_to(DemoSG.hidder_wait)
        await asyncio.create_task(bot_thinking(dialog_manager, user_id))

    elif role == 'searcher':
        if dialog_manager.current_context().dialog_data['mode'] != 'demo':
            is0 = random.randint(0, 9)
            result = 'win' if is0 == 0 else 'lose'
            dialog_manager.current_context().dialog_data['result'] = result
            deposit = dialog_manager.current_context().dialog_data['deposit']
            
            await demo_result_writer(session, deposit, user_id, result)
        else:
            is0 = random.randint(0, 1)
            result = 'win' if is0 == 0 else 'lose'
            dialog_manager.current_context().dialog_data['result'] = result

        await dialog_manager.switch_to(DemoSG.end)


# Exiting from Demo game while play
async def demo_exit(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} exiting from Demo game')
    mode = dialog_manager.current_context().dialog_data['mode']
    result = 'lose'
    dialog_manager.current_context().dialog_data['result'] = result

    if mode == 'public':

        # Process Losing Game
        deposit = dialog_manager.current_context().dialog_data['deposit']
        session = dialog_manager.middleware_data.get('session')
        await demo_result_writer(session, deposit, user_id, result)
        await dialog_manager.switch_to(DemoSG.end)

    elif mode == 'demo':
        await dialog_manager.switch_to(DemoSG.end)

# Exiting from Game after game end
async def demo_end(callback: CallbackQuery,
                   button: Button,
                   dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} end the Demo game')
