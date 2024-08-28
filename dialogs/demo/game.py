import logging
import asyncio
import random

from aiogram import F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner
from redis import asyncio as aioredis

from states import DemoSG, LobbySG, MainSG
from services import (bot_thinking, demo_result_writer, losed_and_deposit,
                      demo_timer, coef_counter, select_role, get_user)
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
    session = dialog_manager.middleware_data.get('session')
    mode = dialog_manager.current_context().dialog_data['mode']
    deposit = dialog_manager.current_context().dialog_data['deposit']

    coef = (await coef_counter(user_id, session))['coef'] 
    prize = coef * deposit
    
    await dialog_manager.reset_stack()
    await r.delete('r_'+str(user_id))

    role = await select_role(session, user_id)
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
    if mode == 'demo':
        if role == 'hidder':
            hidding = FSInputFile(path='img/hidding.jpg')
            msg = await callback.message.answer_photo(photo=hidding,
                                                      caption=i18n.game.hidder(deposit=deposit,
                                                                            coef=coef,
                                                                            prize=prize),
                                                      reply_markup=game_chest_keyboard(i18n))
            # Start timer for 1 minut turn of player
            await asyncio.create_task(demo_timer(dialog_manager,
                                                 user_id, mode,
                                                 game_end_keyboard),
                                      name=f'dt_{user_id}')
        else:
            search = FSInputFile(path='img/search.jpg')
            msg = await callback.message.answer_photo(photo=search,
                                                      caption=i18n.game.wait.searcher(deposit=deposit,
                                                                                   coef=coef,
                                                                                   prize=prize),
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
    else:
    # Checking Players balance - cant play, if havent enough TON
        if (await get_user(session, user_id)).ton >= deposit:
            if role == 'hidder':
                hidding = FSInputFile(path='img/hidding.jpg')
                msg = await callback.message.answer_photo(photo=hidding,
                                                          caption=i18n.game.hidder(deposit=deposit,
                                                                                coef=coef,
                                                                                prize=prize),
                                                          reply_markup=game_chest_keyboard(i18n))
                # Start timer for 1 minut turn of player
                await asyncio.create_task(demo_timer(dialog_manager,
                                                     user_id, mode,
                                                     game_end_keyboard),
                                          name=f'dt_{user_id}')
            else:
                search = FSInputFile(path='img/search.jpg')
                msg = await callback.message.answer_photo(photo=search,
                                                          caption=i18n.game.wait.searcher(deposit=deposit,
                                                                                       coef=coef,
                                                                                       prize=prize),
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
        else:
            msg = await callback.message.answer(text=i18n.notenough.ton())
            await callback.answer()
            await asyncio.sleep(2)
            await r.delete(user_id)
            await r.delete('d_'+str(user_id))
            await dialog_manager.start(state=MainSG.main,
                                       mode=StartMode.RESET_STACK)
            await bot.delete_message(user_id, msg.message_id)

        

# All game in one handler
@demo_router.callback_query(F.data.in_(['first', 'second', 'third', 
                                        'game_exit', 'game_end', 'play_again']),
                            StateFilter(DemoSG.game))
async def main_demo_process(callback: CallbackQuery,
                            state: FSMContext,
                            i18n: TranslatorRunner,
                            dialog_manager: DialogManager,
                            bot: Bot
                            ):
    # Init variables
    r = aioredis.Redis(host='localhost', port=6379)
    user_id = callback.from_user.id
    demo = await r.hgetall('d_' + str(user_id))
    role = str(demo[b'role'], encoding='utf-8')
    mode = str(demo[b'mode'], encoding='utf-8') 
    deposit = float(str(demo[b'deposit'], encoding='utf-8'))
    session = dialog_manager.middleware_data.get('session')
    coef = (await coef_counter(user_id, session))['coef'] 
    prize = coef * deposit
    photo_map = {'first': '1',
                 'second': '2',
                 'third': '3'}
    logger.info(f'User demo: {demo}')

    # It an end of Game - press buttom GAME END
    if callback.data == 'game_end':
        await r.delete(str(user_id))
        await r.delete('d_'+str(user_id))
        await dialog_manager.start(state=MainSG.main,
                                   mode=StartMode.RESET_STACK)
    elif callback.data == 'play_again':
        logger.info(f'User {user_id} want play again in mode: {mode}, deposit: {deposit}')
        await r.delete('d_'+str(user_id))
        target_state = LobbySG.demo_ready if mode == 'demo' else LobbySG.search
        await dialog_manager.start(state=target_state,
                                   mode=StartMode.RESET_STACK,
                                   data={'mode': mode,
                                         'deposit': deposit})
    else:
        # If it Not Exit from Game
        if callback.data != 'game_exit' and callback.data != 'game_end':

            # If User is Hidder
            if role == 'hidder':
                try: 
                    search = FSInputFile(path='img/search.jpg')
                    msg = await callback.message.answer_photo(photo=search,
                                                              caption=i18n.game.hidden(deposit=deposit,
                                                                                       coef=coef,
                                                                                       prize=prize),
                                                              reply_markup=game_exit_keyboard(i18n))
                    await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 5, -1)])
                    
                    # Stop timer
                    task = [task for task in asyncio.all_tasks() if task.get_name() == f'dt_{user_id}']
                    task[0].cancel()

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
                    logger.info(f'User {user_id} ended game as hidder vs Bot in {mode} mode')
                    result = await losed_and_deposit(user_id, session, deposit)
                    await demo_result_writer(session, deposit, user_id, result)
                else:
                    is0 = random.randint(0, 1)
                    result = 'win' if is0 == 0 else 'lose'
                
                if result == 'win':
                    try:
                        if role == 'searcher':
                            win = FSInputFile(path=f'img/win{photo_map[callback.data]}.jpg')
                        else:
                            win = FSInputFile(path=f'img/happy{random.randint(1, 5)}.jpg')
                        msg = await bot.send_photo(photo=win,
                                                   chat_id=user_id,
                                                   caption=i18n.game.youwin(),
                                                   reply_markup=game_end_keyboard(i18n))
                        await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 5, -1)])
                    except TelegramBadRequest as ex:
                        logger.info(f'{ex.message}')
                else:
                    try:
                        if role == 'searcher':
                            lose = FSInputFile(path=f'img/lose{photo_map[callback.data]}.jpg')

                            if callback.data == 'first':
                                chest = random.choice([2, 3])
                            elif callback.data == 'second':
                                chest = random.choice([1, 3])
                            elif callback.data == 'third':
                                chest = random.choice([1, 2])

                            msg = await bot.send_photo(photo=lose,
                                                       chat_id=user_id,
                                                       caption=i18n.game.youlose.searcher(chest=chest),
                                                       reply_markup=game_end_keyboard(i18n))
                        else:
                            lose = FSInputFile(path=f'img/sad{random.randint(1, 5)}.jpg')
                            msg = await bot.send_photo(photo=lose,
                                                       chat_id=user_id,
                                                       caption=i18n.game.youlose(),
                                                       reply_markup=game_end_keyboard(i18n))
                        await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 5, -1)])
                    except TelegramBadRequest as ex:
                        logger.info(f'{ex.message}')
                # Stop timer
                task = [task for task in asyncio.all_tasks() if task.get_name() == f'dt_{user_id}']
                task[0].cancel()
               
        elif callback.data == 'game_exit':
            
            # Count Result
            if mode != 'demo':
                result = 'lose'
                await demo_result_writer(session, deposit, user_id, result)
            else:
                result = 'lose'
            try:
                lose = FSInputFile(path=f'img/sad{random.randint(1, 5)}.jpg')
                msg = await bot.send_photo(photo=lose,
                                           chat_id=user_id,
                                           caption=i18n.game.youlose(),
                                           reply_markup=game_end_keyboard(i18n))
                await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 5, -1)])
            except TelegramBadRequest as ex:
                logger.info(f'{ex.message}')
            try:
                # If game ended before timer is out - stop timer
                task = [task for task in asyncio.all_tasks() if task.get_name() == f'bt_{user_id}']
                task[0].cancel()
            except IndexError:
                logger.info(f'No time yet')


