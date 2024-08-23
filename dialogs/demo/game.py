import logging
import asyncio
import random

from aiogram import F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner
from redis import asyncio as aioredis

from states import DemoSG, LobbySG, MainSG
from services import (bot_thinking, demo_result_writer, losed_and_deposit,
                      demo_timer)
from .keyboard import *

demo_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Create game vs Bot
@demo_router.callback_query(StateFilter(LobbySG.demo_ready))
async def demo_start(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager
                     ):

    user_id = callback.from_user.id

    r = aioredis.Redis(host='localhost', port=6379)
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    mode = dialog_manager.current_context().dialog_data['mode']
    deposit = dialog_manager.current_context().dialog_data['deposit']
    await dialog_manager.reset_stack()
    await r.delete('r_'+str(user_id))

    role = random.choice(['hidder', 'searcher'])
    demo = {
            'owner': user_id,
            'mode': mode,
            'deposit': deposit,
            'role': role
            }

    await r.hmset('d_' + str(user_id), demo)
    state = dialog_manager.middleware_data.get('state')
    await state.set_state(DemoSG.game)

    # Checking users Role in that game
    if role == 'hidder':
        msg = await callback.message.answer(text=i18n.game.hidder(),
                                            reply_markup=game_chest_keyboard(i18n))
        # Start timer for 1 minut turn of player
        await asyncio.create_task(demo_timer(dialog_manager,
                                             user_id,
                                             mode),
                                  name=f'dt_{user_id}')
    else:
        msg = await callback.message.answer(text=i18n.game.wait.searcher(),
                                            reply_markup=game_exit_keyboard(i18n))
        # Turn timer for bot
        await asyncio.create_task(bot_thinking(dialog_manager,
                                               user_id, role,
                                               demo_result_writer,
                                               game_end_keyboard,
                                               game_chest_keyboard),
                                  name=f'bt_{user_id}')
    try:
        await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 10, -1)])
    except TelegramBadRequest:
        await callback.answer()
        

# All game in one handler
@demo_router.callback_query(F.data.in_(['first', 'second', 'third', 
                                        'game_exit', 'game_end']),
                            StateFilter(DemoSG.game))
async def main_demo_process(callback: CallbackQuery,
                            state: FSMContext,
                            i18n: TranslatorRunner,
                            dialog_manager: DialogManager,
                            bot: Bot
                            ):
    
    # It an end of Game - press buttom GAME END
    if callback.data == 'game_end':
        await dialog_manager.start(state=MainSG.main,
                                   mode=StartMode.RESET_STACK)
    else:
        # Init variables

        r = aioredis.Redis(host='localhost', port=6379)
        user_id = callback.from_user.id
        demo = await r.hgetall('d_' + str(user_id))
        role = str(demo[b'role'], encoding='utf-8')
        mode = str(demo[b'mode'], encoding='utf-8') 
        deposit = float(str(demo[b'deposit'], encoding='utf-8'))
        session = dialog_manager.middleware_data.get('session')
        
        logger.info(f'User demo: {demo}')
        
        # If it Not Exit from Game
        if callback.data != 'game_exit' and callback.data != 'game_end':

            # If User is Hidder
            if role == 'hidder':
                try: 
                    msg = await callback.message.edit_text(text=i18n.game.hidden(),
                                                           reply_markup=game_exit_keyboard(i18n))
                    await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 5, -1)])
                except TelegramBadRequest:
                    await callback.answer()
                await asyncio.create_task(bot_thinking(dialog_manager,
                                                       user_id, role,
                                                       demo_result_writer,
                                                       game_end_keyboard,
                                                       game_chest_keyboard),
                                          name=f'bt_{user_id}')
            # If User is Searcher
            else:
                # Count Result
                if mode != 'demo':
                    result = await losed_and_deposit(user_id, session, deposit)
                    await demo_result_writer(session, deposit, user_id, result)
                else:
                    is0 = random.randint(0, 1)
                    result = 'win' if is0 == 0 else 'lose'
                
                if result == 'win':
                    try:
                        msg = await bot.send_message(chat_id=user_id,
                                                     text=i18n.game.youwin(deposit=deposit),
                                                     reply_markup=game_end_keyboard(i18n))
                        await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 5, -1)])
                    except TelegramBadRequest as ex:
                        logger.info(f'{ex.message}')
                else:
                    try:
                        msg = await bot.send_message(chat_id=user_id,
                                                     text=i18n.game.youlose(deposit=deposit),
                                                     reply_markup=game_end_keyboard(i18n))
                        await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 5, -1)])
                    except TelegramBadRequest as ex:
                        logger.info(f'{ex.message}')
                await r.delete('d_' + str(user_id))
               
        elif callback.data == 'game_exit':
            
            # Count Result
            if mode != 'demo':
                result = 'lose'
                await demo_result_writer(session, deposit, user_id, result)
            else:
                result = 'lose'
            
            try:
                msg = await bot.send_message(chat_id=user_id,
                                             text=i18n.game.youlose(deposit=deposit),
                                             reply_markup=game_end_keyboard(i18n))
                await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 5, -1)])
            except TelegramBadRequest as ex:
                logger.info(f'{ex.message}')
            
            await r.delete('d_' + str(user_id))

            # If game ended before timer is out - stop timer
            task = [task for task in asyncio.all_tasks() if task.get_name() == f'bt_{user_id}']
            task[0].cancel()


