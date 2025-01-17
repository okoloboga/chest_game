import logging
import asyncio
import random

from aiogram.methods import delete_message
from aiogram.types import FSInputFile
from aiogram import F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner
from redis import asyncio as aioredis
from ton.client.function_methods import Key

from states import GameSG, LobbySG, MainSG
from services import (room_to_game, game_result_writer, turn_timer, 
                      coef_counter, get_user, write_as_guest, promocode_usage)
from .keyboard import *

game_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Created Room or Query - now un GameSG, without Dialog
# Returning Game menu for HIdder or Searcher 
# And delete last message
@game_router.callback_query(StateFilter(LobbySG.game_confirm))
async def game_start(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager
                     ):

    r = aioredis.Redis(host='localhost', port=6379)
    room = dialog_manager.current_context().dialog_data['room']
    logger.info(f'Room is {room}')
    try:
        owner = str(room[b'owner'], encoding='utf-8')
    except TypeError:    
        owner = room
    session = dialog_manager.middleware_data.get('session')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    bot: Bot = dialog_manager.middleware_data.get('bot')

    user_id = callback.from_user.id
    result = await room_to_game(session, user_id, owner)

    logger.info(f'User {callback.from_user.id} start game as {result}')

    # Getting hidder from Game data
    user_game_str = str(await r.get(user_id), encoding='utf-8')
    logger.info(f'user_game_str: {user_game_str}')
    user_game = await r.hgetall(user_game_str)
    logger.info(f'user_game is {user_game}')
    
    # If Game owner didn't create Game yet
    if len(user_game) > 0:

        await dialog_manager.reset_stack()
        hidder = int(str(user_game[b'hidder'], encoding='utf-8'))
        state = dialog_manager.middleware_data.get('state')
        session = dialog_manager.middleware_data.get('session')
        await state.set_state(GameSG.main)
        coef = (await coef_counter(user_id, session))['coef']
        deposit = float(str(user_game[b'deposit'], encoding='utf-8'))
        promo = await promocode_usage(session, user_id)
        prize = 2 * deposit if promo else deposit * coef 
        
        # Checking Players balance - cant play, if havent enough TON
        if (await get_user(session, user_id)).ton >= deposit:
        # Checking users Role in that game
            if hidder == int(user_id):
                hidding = FSInputFile(path='img/hidding.jpg')
                msg = await bot.send_photo(photo=hidding,
                                           chat_id=user_id,
                                           caption=i18n.game.hidder(deposit=deposit,
                                                                    coef=coef,
                                                                    prize=prize),
                                           reply_markup=game_chest_keyboard(i18n))
            else:
                search = FSInputFile(path='img/search.jpg')
                msg = await bot.send_photo(photo=search,
                                           chat_id=user_id,
                                           caption=i18n.game.wait.searcher(deposit=deposit,
                                                                           coef=coef,
                                                                           prize=prize))
            await asyncio.sleep(1)
            try:
                await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, 
                                                                         msg.message_id - 10, 
                                                                         -1)])
            except TelegramBadRequest:
                await callback.answer()
 
            task = [task for task in asyncio.all_tasks() if task.get_name() == f't_{owner}']
            logger.info(f'Timer for game {user_game_str}: {task}')
            if len(task) == 0:
                # Turn timer for each player
                await asyncio.create_task(turn_timer(dialog_manager, 
                                                     user_game_str[2:],
                                                     hidder,
                                                     game_end_keyboard),
                                          name=f't_{user_game_str[2:]}')
        else:
            msg = await callback.message.answer(text=i18n.notenough.ton())
            await callback.answer()
            await asyncio.sleep(2)
            await r.delete(user_id)
            await r.delete('g_'+str(owner))
            await dialog_manager.start(state=MainSG.main,
                                       mode=StartMode.RESET_STACK)
            await bot.delete_message(user_id, msg.message_id)
    elif await r.exists('r_' + owner) != 0 or await r.exists('pr_' + owner) != 0:
        msg = await callback.message.answer(text=i18n.waiting.foropponent())
        await asyncio.sleep(2)
        await bot.delete_message(user_id, msg.message_id)
        

# All game in one handler
@game_router.callback_query(F.data.in_(['first', 'second', 'third', 
                                        'game_end', 'play_again']),
                            StateFilter(GameSG.main))
async def main_game_process(callback: CallbackQuery,
                            state: FSMContext,
                            i18n: TranslatorRunner,
                            dialog_manager: DialogManager,
                            bot: Bot
                            ):
    # Init variables

    r = aioredis.Redis(host='localhost', port=6379)
    user_id = callback.from_user.id
    user_game_str = await r.get(user_id)

    logger.info(f'user_game_str: {user_game_str}')

    user_game = await r.hgetall(str(user_game_str, encoding='utf-8'))
    
    logger.info(f'user_game: {user_game}')
    try:
        owner = int(str(user_game[b'owner'], encoding='utf-8'))
        guest = int(str(user_game[b'guest'], encoding='utf-8'))
        enemy = owner if guest == user_id else guest
        hidder = str(user_game[b'hidder'], encoding='utf-8') 
        searcher = guest if int(hidder) == int(owner) else owner
        session = dialog_manager.middleware_data.get('session')
        mode = str(user_game[b'mode'], encoding='utf-8')

        coef = (await coef_counter(user_id, session))['coef'] 
        deposit = float(str(user_game[b'deposit'], encoding='utf-8'))
        prize = coef * deposit

        logger.info(f'Hidder: {hidder}, Searcher: {searcher}')
        logger.info(f'Owner: {owner}, Guest: {guest}')
        logger.info(f'User: {user_id}, Enemy: {enemy}')
    except KeyError:
        logger.info(f'Leave game {user_game_str}')

    # It an end of Game - press buttom GAME END
    if callback.data == 'game_end':
        await r.delete(str(user_id))
        try:
            await r.delete('g_'+str(owner))
        except UnboundLocalError:
            logger.info('Game not exists')
        await dialog_manager.start(state=MainSG.main,
                                   mode=StartMode.RESET_STACK)
    elif callback.data == 'play_again':
        try:
            if mode == 'private' and int(owner) != int(user_id):
                logger.info(f'User {user_id} want to play again in {mode} with owner {owner}')
                logger.info(f"exists? - {await r.hgetall('pr_' + str(owner))}")
                if await r.exists('pr_' + str(owner)) != 0:
                    room = await r.hgetall('pr_' + str(owner))
                    await write_as_guest(room, user_id)
                    await dialog_manager.start(LobbySG.game_ready,
                                               mode=StartMode.RESET_STACK,
                                               data={'game_id': owner,
                                                     'mode': mode,
                                                     'deposit': deposit})
                else: 
                    msg = await callback.message.answer(text=i18n.waiting.foropponent())
                    await asyncio.sleep(2)
                    await bot.delete_message(user_id, msg.message_id)
                    await callback.answer()
            else:
                await dialog_manager.start(state=LobbySG.search,
                                           mode=StartMode.RESET_STACK,
                                           data={'game_id': owner,
                                                 'mode': mode,
                                                 'deposit': deposit})
        except UnboundLocalError:
            msg = await callback.message.answer(text=i18n.opponent.leaved())
            await asyncio.sleep(2)
            await bot.delete_message(user_id, msg.message_id)
            await dialog_manager.start(state=MainSG.main,
                                       mode=StartMode.RESET_STACK)
    else:        
        # If it Not Exit from Game
        if callback.data != 'game_exit' and callback.data != 'game_end':

            # If User is Hidder
            if int(user_id) == int(hidder):
                 
                # Writing to Redis database
                user_game[b'target'] = callback.data
                promo = await promocode_usage(session, user_id)
                prize = 2 * deposit if promo else deposit * float(coef) 

                logger.info(f'user_game after hidding: {user_game}')
                await r.hmset(user_game_str, user_game)
                await bot.delete_message(chat_id=user_id,
                                         message_id=callback.message.message_id)         
                search = FSInputFile(path='img/search.jpg')
                await bot.send_photo(photo=search,
                                     chat_id=user_id,                                          
                                     caption=i18n.game.hidden(deposit=deposit,
                                                              coef=coef,
                                                              prize=prize))
                # Give turn to Searcher
                select = FSInputFile(path='img/select.jpg')
                msg_enemy = await bot.send_photo(photo=select,
                                                 chat_id=searcher, 
                                                 caption=i18n.game.searcher(deposit=deposit,
                                                                            coef=coef,
                                                                            prize=prize),
                                                 reply_markup=game_chest_keyboard(i18n))
                await asyncio.sleep(1)
                try:
                    await bot.delete_messages(searcher, [msg for msg in range(msg_enemy.message_id - 1, 
                                                                              msg_enemy.message_id - 10, 
                                                                              -1)])
                except TelegramBadRequest:
                    await callback.answer()

                # Switching timer from hidder to searcher
                task = [task for task in asyncio.all_tasks() if task.get_name() == f't_{owner}']
                task[0].cancel()
                await asyncio.create_task(turn_timer(dialog_manager,
                                                     owner,
                                                     searcher,
                                                     game_end_keyboard),
                                          name=f't_{owner}')

            # If User is Searcher
            else:
                target = str(user_game[b'target'], encoding='utf-8')
                deposit = str(user_game[b'deposit'], encoding='utf-8')
                logger.info(f'Target is {target}')
                photo_map = {'first': '1',
                             'second': '2',
                             'third': '3'}

                # Checking for success or not 
                if target == callback.data:
                    win = FSInputFile(path=f'img/win{photo_map[target]}.jpg')
                    await bot.delete_message(chat_id=user_id,
                                             message_id=callback.message.message_id)           
                    await bot.send_photo(photo=win,
                                         chat_id=user_id,
                                         caption=i18n.game.youwin(),
                                         reply_markup=game_end_keyboard(i18n)) 
                    # Send notification to Hidder
                    lose = FSInputFile(path=f'img/sad{random.randint(1, 5)}.jpg')
                    msg_enemy = await bot.send_photo(photo=lose,
                                                     chat_id=hidder, 
                                                     caption=i18n.game.youlose(),
                                                     reply_markup=game_end_keyboard(i18n))
                    await asyncio.sleep(1)
                    try:
                        await bot.delete_messages(hidder, [msg for msg in range(msg_enemy.message_id - 1, 
                                                                                msg_enemy.message_id - 10, 
                                                                                -1)])
                    except TelegramBadRequest:
                        await callback.answer()
                    
                    await game_result_writer(session,
                                             int(owner), 
                                             float(deposit), 
                                             winner_id=int(searcher),
                                             loser_id=int(hidder))

                else:
                    target_map = {'first': 1,
                                  'second': 2,
                                  'third': 3}
                    lose = FSInputFile(path=f'img/lose{photo_map[callback.data]}.jpg')
                    await bot.delete_message(chat_id=user_id,
                                             message_id=callback.message.message_id)       
                    await bot.send_photo(photo=lose,
                                         chat_id=user_id,
                                         caption=i18n.game.youlose.searcher(chest=target_map[target]),
                                         reply_markup=game_end_keyboard(i18n))
                    # Send notification to Hidder
                    win = FSInputFile(path=f'img/happy{random.randint(1, 5)}.jpg')
                    msg_enemy = await bot.send_photo(photo=win,
                                                     chat_id=hidder, 
                                                     caption=i18n.game.youwin(),
                                                     reply_markup=game_end_keyboard(i18n))
                    await asyncio.sleep(1)
                    try:
                        await bot.delete_messages(hidder, [msg for msg in range(msg_enemy.message_id - 1, 
                                                                                msg_enemy.message_id - 10, 
                                                                                -1)]) 
                    except TelegramBadRequest:
                        await callback.answer()
                                       
                    await game_result_writer(session,
                                             int(owner), 
                                             float(deposit), 
                                             winner_id=int(hidder),
                                             loser_id=int(searcher))

                # If game ended before timer is out - stop timer
                task = [task for task in asyncio.all_tasks() if task.get_name() == f't_{owner}']
                task[0].cancel()

