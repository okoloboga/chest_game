import logging
import random

from aiogram import Router
from aiogram.types import CallbackQuery, Message, callback_query
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from fluentogram import TranslatorRunner

from states import DemoSG, MainSG
from services import demo_result_writer


lobby_router = Router()

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
    dialog_manager.current_context().dialog_data['role'] = role

    if role == 'hidder':
        await dialog_manager.switch_to(DemoSG.hidder_active)
    elif role == 'searcher':
        await dialog_manager.switch_to((DemoSG.searcher_wait))


# Process Selecting Chest
async def select_chest(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager):

    user_id = callback.from_user.id
    logger.info(f'User {user_id} selected the Chest')
    role = dialog_manager.current_context().dialog_data['role']

    if role = 'hidder':
        await dialog_manager.switch_to(DemoSG.hidder_wait)
    elif role = 'searcher':
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
